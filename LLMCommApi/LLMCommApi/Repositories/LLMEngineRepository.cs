using System.Text;
using System.Text.Json;
using LLMCommApi.Entities;
using LLMCommApi.Settings;
using Microsoft.Extensions.Options;
using RabbitMQ.Client;
using RabbitMQ.Client.Events;

namespace LLMCommApi.Repositories;

public class LLMEngineRepository : ILLMEngineRepository
{
    
    private readonly LLMCommSettings _commSettings;
    private IConnection _connection;
    private IModel _channel;
    private EventingBasicConsumer _consumer;
    
    
    public LLMEngineRepository(IOptions<LLMCommSettings> commSettings)
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

    
    public Task<DataUpdateStatus> RequestDataUpdateAsync()
    {
        var taskCompletionSource = new TaskCompletionSource<DataUpdateStatus>();
        var requestQueue = _commSettings.LLMUpdateQueue;
        var replyQueue = _commSettings.LLMStatusQueue;
        
        if(!_connection.IsOpen) InitConnection();
        _channel.QueueDeclare(queue: replyQueue, durable: false, exclusive: false, autoDelete: false, arguments: null);
        
        // listens to reply
        _consumer = new EventingBasicConsumer(_channel);
        _consumer.Received += (_, e) =>
        {
            var status = Encoding.UTF8.GetString(e.Body.ToArray());
            Console.WriteLine($"received from {replyQueue}: {status}");
            
            var dataUpdateStatus = new DataUpdateStatus
            {
                Status = status,
                CreatedDate = DateTimeOffset.Now
            };
            
            Dispose();
            taskCompletionSource.SetResult(dataUpdateStatus);
        };
        _channel.BasicConsume(
            queue: replyQueue,
            autoAck: true,
            consumer: _consumer
        );
        Console.WriteLine($"consumer started for {replyQueue}");
        
        SendMessage("all-data-source-param", requestQueue, replyQueue);
        
        return taskCompletionSource.Task;
    }


    private void SendMessage(string prompt, string requestQueue, string replyQueue)
    {
        var messageBytes = Encoding.UTF8.GetBytes(prompt);
        var props = _channel.CreateBasicProperties();
        props.ReplyTo = replyQueue;
        _channel.BasicPublish(
            exchange: "",
            routingKey: requestQueue,
            basicProperties: props,
            body: messageBytes
        );
        Console.WriteLine($"publish message to {requestQueue}");
    }
    
    
    private void Dispose()
    {
        _channel.Dispose();
        _connection.Dispose();
    }
    
    
}

