namespace LLMCommApi.Entities;

public record PromptReply
{
    public string? Reply { get; init; }
    public DateTimeOffset CreatedDate { get; init; }
}