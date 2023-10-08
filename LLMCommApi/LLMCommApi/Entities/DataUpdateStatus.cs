namespace LLMCommApi.Entities;

public record DataUpdateStatus
{
    public string Status { get; init; }
    public DateTimeOffset CreatedDate { get; init; }
}