using Newtonsoft.Json;

namespace LLMCommApi.Entities;

public record LlmStatus
{
    [JsonProperty("status_code")]
    public int Code { get; init; }
    
    [JsonProperty("status_message")]
    public string Status { get; init; }
}