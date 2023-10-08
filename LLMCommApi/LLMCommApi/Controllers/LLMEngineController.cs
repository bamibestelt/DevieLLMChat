using LLMCommApi.Dto;
using LLMCommApi.Entities;
using LLMCommApi.Repositories;
using Microsoft.AspNetCore.Mvc;

namespace LLMCommApi.Controllers;


/**
* API endpoints:
* POST Question ===> Result: Answer
* POST Data Update ===> Result: Status
*/

[ApiController]
[Route("llm")]
public class LLMEngineController : ControllerBase
{
    private readonly ILogger<LLMEngineController> _logger;
    private readonly ILLMEngineRepository _repository;

    
    public LLMEngineController(ILogger<LLMEngineController> logger, ILLMEngineRepository repository)
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
    public async Task<DataUpdateStatus> RequestDataUpdateAsync()
    {
        _logger.LogInformation("RequestDataUpdateAsync");
        
        // todo ping-pong from and until certain status
        var status = await _repository.RequestDataUpdateAsync();
        Console.WriteLine($"status: {status.Status}");
        
        return status;
    }
}