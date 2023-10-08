namespace LLMCommApi.Dto;

public record PromptReplyDto
{
    public string Reply { get; init; }
    public DateTimeOffset CreatedDate { get; init; }    
}