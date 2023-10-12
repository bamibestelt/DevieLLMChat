using LLMCommApi.Entities;

namespace LLMCommApi.Repositories;

public interface ILlmEngineRepository
{
    Task<PromptReply> PostPromptAsync(Prompt prompt);
    Task RequestDataUpdateAsync();
    Task ConsumeLlmStatus();
    string LlmStatusJson { get; set; }
}