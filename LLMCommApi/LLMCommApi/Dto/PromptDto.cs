using System.ComponentModel.DataAnnotations;

namespace LLMCommApi.Dto;

public record PromptDto
{
    [Required]
    public string PromptText { get; init; }
}