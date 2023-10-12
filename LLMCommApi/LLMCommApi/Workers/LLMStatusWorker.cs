using LLMCommApi.Repositories;

namespace LLMCommApi.Workers;

public class LlmStatusWorker : BackgroundService
{
    private readonly ILogger<LlmStatusWorker> _logger;
    private readonly ILlmEngineRepository _repository;
    
    
    public LlmStatusWorker(ILogger<LlmStatusWorker> logger, ILlmEngineRepository repository)
    {
        _logger = logger;
        _repository = repository;
    }
    
    
    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        _logger.LogInformation("LLMStatusWorker => ExecuteAsync");
        await _repository.ConsumeLlmStatus();
    }
    
    
}