using System.ComponentModel.DataAnnotations;

namespace LLMCommApi.Entities;

public record Prompt
{
    [Required]
    public string PromptText { get; init; }
}