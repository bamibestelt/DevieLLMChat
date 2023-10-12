using System.Text;
using LLMCommApi.Entities;
using LLMCommApi.Settings;
using Microsoft.Extensions.Options;
using RabbitMQ.Client;
using RabbitMQ.Client.Events;

namespace LLMCommApi.Repositories;

public class LlmEngineRepository : ILlmEngineRepository
{
    
    private readonly LLMCommSettings _commSettings;
    private EventingBasicConsumer _consumer;
    private IConnection _connection;
    private IModel _channel;
    
    
    public LlmEngineRepository(IOptions<LLMCommSettings> commSettings)
    {
        _commSettings = commSettings.Value;
        InitConnection();
    }

    
    private void InitConnection()
    {
        Console.WriteLine("InitConnection");
        
        var factory = new ConnectionFactory { HostName = _commSettings.Host };
        _connection = factory.CreateConnection();
        _channel = _connection.CreateModel();
        
        Console.WriteLine("connection initialized");
    }


    public Task<PromptReply> PostPromptAsync(Prompt prompt)
    {
        var taskCompletionSource = new TaskCompletionSource<PromptReply>();
        var requestQueue = _commSettings.PromptQueue;
        var replyQueue = _commSettings.LLMReplyQueue;
        
        if(!_connection.IsOpen) InitConnection();
        _channel.QueueDeclare(queue: replyQueue, durable: false, exclusive: false, autoDelete: false, arguments: null);
        
        // listens to reply
        _consumer = new EventingBasicConsumer(_channel);
        _consumer.Received += (_, e) =>
        {
            var reply = Encoding.UTF8.GetString(e.Body.ToArray());
            Console.WriteLine($"received from {replyQueue}: {reply}");
            
            var promptReply = new PromptReply
            {
                Reply = reply,
                CreatedDate = DateTimeOffset.Now
            };
            
            Dispose();
            taskCompletionSource.SetResult(promptReply);
        };
        _channel.BasicConsume(
            queue: replyQueue,
            autoAck: true,
            consumer: _consumer
        );
        Console.WriteLine($"consumer started for {replyQueue}");
        
        // send request
        SendMessage(prompt.PromptText, requestQueue, replyQueue);
        
        return taskCompletionSource.Task;
    }

    
    public async Task RequestDataUpdateAsync()
    {
        var requestQueue = _commSettings.LLMUpdateQueue;
        SendMessage("all-data-source-param", requestQueue);
    }


    private void SendMessage(string prompt, string requestQueue, string replyQueue = "")
    {
        var messageBytes = Encoding.UTF8.GetBytes(prompt);
        var props = _channel.CreateBasicProperties();
        if(replyQueue.Length > 0)
            props.ReplyTo = replyQueue;
        _channel.BasicPublish(
            exchange: "",
            routingKey: requestQueue,
            basicProperties: props,
            body: messageBytes
        );
        Console.WriteLine($"publish message to {requestQueue}");
    }


    public async Task ConsumeLlmStatus()
    {
        var statusQueue = _commSettings.LLMStatusQueue;
        
        if(!_connection.IsOpen) InitConnection();
        _channel.QueueDeclare(queue: statusQueue, durable: false, 
            exclusive: false, autoDelete: false, arguments: null);
        
        _consumer = new EventingBasicConsumer(_channel);
        _consumer.Received += (_, e) =>
        {
            var status = Encoding.UTF8.GetString(e.Body);
            Console.WriteLine($"received from {statusQueue}: {status}");
            LlmStatusJson = status;
        };
        
        _channel.BasicConsume(
            queue: statusQueue,
            autoAck: true,
            consumer: _consumer
        );
        
        Console.WriteLine($"consumer started for {statusQueue}");
    }

    public string LlmStatusJson { get; set; }


    private void Dispose()
    {
        _channel.Dispose();
        _connection.Dispose();
    }
    
    
}

