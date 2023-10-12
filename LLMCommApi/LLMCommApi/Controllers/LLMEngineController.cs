using System.Text;
using LLMCommApi.Dto;
using LLMCommApi.Entities;
using LLMCommApi.Repositories;
using Microsoft.AspNetCore.Mvc;
using Newtonsoft.Json;

namespace LLMCommApi.Controllers;


[ApiController]
[Route("llm")]
public class LlmEngineController : ControllerBase
{
    private readonly ILogger<LlmEngineController> _logger;
    private readonly ILlmEngineRepository _repository;

    
    public LlmEngineController(ILogger<LlmEngineController> logger, ILlmEngineRepository repository)
    {
        _logger = logger;
        _repository = repository;
    }
    

    [HttpPost("prompt")]
    public async Task<ActionResult<PromptReply>> PostPromptAsync(PromptDto promptDto)
    {
        _logger.LogInformation("PostPromptAsync");
        
        Prompt prompt = new()
        {
            PromptText = promptDto.PromptText
        };
        
        var reply = await _repository.PostPromptAsync(prompt);
        Console.WriteLine($"reply: {reply.Reply}");
        
        return reply.Reply == null ? NotFound() : reply;
    }
    
    
    [HttpPost("update")]
    public async Task<IActionResult> RequestDataUpdateAsync(CancellationToken cancellationToken)
    {
        _logger.LogInformation("RequestDataUpdateAsync");
        
        await _repository.RequestDataUpdateAsync();
        
        Response.ContentType = "text/event-stream";
        Response.Headers.Add("Cache-Control", "no-cache");
        var tempStatusCode = 0;
        
        try
        {
            while (tempStatusCode > -1)
            {
                if (cancellationToken.IsCancellationRequested)
                {
                    break;
                }

                var statusJson = _repository.LlmStatusJson;
                Console.WriteLine(statusJson);
                
                var status = JsonConvert.DeserializeObject<LlmStatus>(statusJson);
                tempStatusCode = status?.Code ?? -1;
                
                var data = Encoding.UTF8.GetBytes(statusJson);
                await Response.Body.WriteAsync(data, cancellationToken);
                await Response.Body.FlushAsync(cancellationToken);
                
                await Task.Delay(1000, cancellationToken);
            }
        }
        catch (OperationCanceledException)
        {
            // Cancellation token was triggered, so we stop sending events
        }
        finally
        {
            Response.Body.Close();
        }

        return Ok();
    }
}