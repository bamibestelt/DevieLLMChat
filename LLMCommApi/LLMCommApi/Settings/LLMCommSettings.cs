namespace LLMCommApi.Settings;

public class LLMCommSettings
{
    public string Host { get; set; }
    public string PromptQueue { get; set; }
    public string LLMReplyQueue { get; set; }
    public string LLMUpdateQueue { get; set; }
    public string LLMStatusQueue { get; set; }
}