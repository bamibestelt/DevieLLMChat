using LLMCommApi.Dto;
using LLMCommApi.Entities;

namespace LLMCommApi;

public static class Extensions
{
    public static PromptReplyDto AsDto(this PromptReply promptReply)
    {
        return new PromptReplyDto
        {
            Reply = promptReply.Reply,
            CreatedDate = promptReply.CreatedDate
        };
    }
}