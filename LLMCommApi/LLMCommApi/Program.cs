using LLMCommApi.Repositories;
using LLMCommApi.Settings;
using LLMCommApi.Workers;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddCors(options =>
{
    options.AddDefaultPolicy(builder => builder.AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader());
});
builder.Services.Configure<LLMCommSettings>(builder.Configuration.GetSection("RabbitMQ"));

// Add services to the container.
builder.Services.AddSingleton<ILlmEngineRepository, LlmEngineRepository>();
builder.Services.AddControllers();
builder.Services.AddHostedService<LlmStatusWorker>();

// Learn more about configuring Swagger/OpenAPI at https://aka.ms/aspnetcore/swashbuckle
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

var app = builder.Build();

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseCors();

app.UseHttpsRedirection();

app.UseAuthorization();

app.MapControllers();

app.Run();