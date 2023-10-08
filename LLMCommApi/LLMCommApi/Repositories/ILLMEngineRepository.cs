using LLMCommApi.Entities;

namespace LLMCommApi.Repositories;

public interface ILLMEngineRepository
{
    Task<PromptReply> PostPromptAsync(Prompt prompt);
    Task<DataUpdateStatus> RequestDataUpdateAsync();
}