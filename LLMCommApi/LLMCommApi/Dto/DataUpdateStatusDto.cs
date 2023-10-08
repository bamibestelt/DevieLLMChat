namespace LLMCommApi.Dto;

public record DataUpdateStatusDto
{
    public string Status { get; init; }
    public DateTimeOffset CreatedDate { get; init; }
}