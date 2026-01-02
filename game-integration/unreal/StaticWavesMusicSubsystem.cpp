/**
 * StaticWaves Music Subsystem Implementation
 */

#include "StaticWavesMusicSubsystem.h"
#include "WebSocketsModule.h"
#include "IWebSocket.h"

UStaticWavesMusicSubsystem::UStaticWavesMusicSubsystem()
{
    // Set default context
    CurrentContext = FMusicContext();
    TargetContext = CurrentContext;
}

void UStaticWavesMusicSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);

    // Register tick function
    TickerHandle = FTSTicker::GetCoreTicker().AddTicker(
        FTickerDelegate::CreateUObject(this, &UStaticWavesMusicSubsystem::Tick)
    );

    UE_LOG(LogTemp, Log, TEXT("[StaticWaves] Subsystem initialized"));
}

void UStaticWavesMusicSubsystem::Deinitialize()
{
    // Remove ticker
    FTSTicker::GetCoreTicker().RemoveTicker(TickerHandle);

    // Disconnect
    Disconnect();

    Super::Deinitialize();
}

void UStaticWavesMusicSubsystem::Connect(const FString& InServerURL)
{
    if (bIsConnected)
    {
        UE_LOG(LogTemp, Warning, TEXT("[StaticWaves] Already connected"));
        return;
    }

    ServerURL = InServerURL;

    // Create WebSocket
    if (!FModuleManager::Get().IsModuleLoaded("WebSockets"))
    {
        FModuleManager::Get().LoadModule("WebSockets");
    }

    WebSocket = FWebSocketsModule::Get().CreateWebSocket(ServerURL);

    // Bind callbacks
    WebSocket->OnConnected().AddUObject(this, &UStaticWavesMusicSubsystem::OnConnected);
    WebSocket->OnConnectionError().AddUObject(this, &UStaticWavesMusicSubsystem::OnConnectionError);
    WebSocket->OnClosed().AddUObject(this, &UStaticWavesMusicSubsystem::OnClosed);
    WebSocket->OnMessage().AddUObject(this, &UStaticWavesMusicSubsystem::OnMessage);
    WebSocket->OnRawMessage().AddUObject(this, &UStaticWavesMusicSubsystem::OnRawMessage);

    // Connect
    WebSocket->Connect();

    UE_LOG(LogTemp, Log, TEXT("[StaticWaves] Connecting to %s..."), *ServerURL);
}

void UStaticWavesMusicSubsystem::Disconnect()
{
    if (!bIsConnected) return;

    if (WebSocket.IsValid())
    {
        WebSocket->Close();
        WebSocket.Reset();
    }

    bIsConnected = false;
    UE_LOG(LogTemp, Log, TEXT("[StaticWaves] Disconnected"));
}

void UStaticWavesMusicSubsystem::SetMusicContext(FMusicContext Context)
{
    CurrentContext = Context;
    TargetContext = Context;
    TransitionAlpha = 1.0f;

    SendControlUpdate();
}

void UStaticWavesMusicSubsystem::TransitionToContext(FMusicContext Context, float TransitionTime)
{
    TargetContext = Context;
    TransitionDuration = FMath::Max(0.1f, TransitionTime);
    TransitionAlpha = 0.0f;
}

void UStaticWavesMusicSubsystem::SetExploration()
{
    FMusicContext Context;
    Context.Energy = 0.3f;
    Context.Tension = 0.1f;
    Context.Darkness = 0.2f;
    Context.Complexity = 0.4f;
    TransitionToContext(Context);
}

void UStaticWavesMusicSubsystem::SetCombat()
{
    FMusicContext Context;
    Context.Energy = 0.9f;
    Context.Tension = 0.8f;
    Context.Darkness = 0.6f;
    Context.Complexity = 0.7f;
    TransitionToContext(Context);
}

void UStaticWavesMusicSubsystem::SetBoss()
{
    FMusicContext Context;
    Context.Energy = 1.0f;
    Context.Tension = 0.95f;
    Context.Darkness = 0.8f;
    Context.Complexity = 0.9f;
    TransitionToContext(Context);
}

void UStaticWavesMusicSubsystem::SetPuzzle()
{
    FMusicContext Context;
    Context.Energy = 0.4f;
    Context.Tension = 0.5f;
    Context.Darkness = 0.3f;
    Context.Complexity = 0.6f;
    TransitionToContext(Context);
}

void UStaticWavesMusicSubsystem::SetVictory()
{
    FMusicContext Context;
    Context.Energy = 0.7f;
    Context.Tension = 0.2f;
    Context.Darkness = 0.1f;
    Context.Complexity = 0.5f;
    TransitionToContext(Context);
}

void UStaticWavesMusicSubsystem::PushMusicEvent(FName EventName, float Intensity)
{
    // Simple event mapping
    if (EventName == "combat_start")
    {
        SetCombat();
    }
    else if (EventName == "boss_enter")
    {
        SetBoss();
    }
    else if (EventName == "puzzle_start")
    {
        SetPuzzle();
    }
    else if (EventName == "victory")
    {
        SetVictory();
    }
    else
    {
        // Generic intensity adjustment
        FMusicContext Context = CurrentContext;
        Context.Tension = FMath::Clamp(Intensity, 0.0f, 1.0f);
        TransitionToContext(Context, 0.5f);
    }
}

void UStaticWavesMusicSubsystem::SendControlUpdate()
{
    if (!bIsConnected || !WebSocket.IsValid()) return;

    FString JsonString = CurrentContext.ToJson();
    WebSocket->Send(JsonString);

    UE_LOG(LogTemp, Verbose, TEXT("[StaticWaves] Sent: %s"), *JsonString);
}

void UStaticWavesMusicSubsystem::OnConnected()
{
    bIsConnected = true;
    UE_LOG(LogTemp, Log, TEXT("[StaticWaves] Connected successfully"));

    // Send initial context
    SendControlUpdate();
}

void UStaticWavesMusicSubsystem::OnConnectionError(const FString& Error)
{
    bIsConnected = false;
    UE_LOG(LogTemp, Error, TEXT("[StaticWaves] Connection error: %s"), *Error);
}

void UStaticWavesMusicSubsystem::OnClosed(int32 StatusCode, const FString& Reason, bool bWasClean)
{
    bIsConnected = false;
    UE_LOG(LogTemp, Log, TEXT("[StaticWaves] Connection closed: %s (Code: %d)"), *Reason, StatusCode);
}

void UStaticWavesMusicSubsystem::OnMessage(const FString& Message)
{
    // Handle text messages from server (if any)
    UE_LOG(LogTemp, Verbose, TEXT("[StaticWaves] Received message: %s"), *Message);
}

void UStaticWavesMusicSubsystem::OnRawMessage(const void* Data, SIZE_T Size, SIZE_T BytesRemaining)
{
    // Handle binary audio data
    // In a full implementation, this would:
    // 1. Convert PCM data to Unreal audio format
    // 2. Queue for playback through USoundWave or audio component
    // 3. Manage audio buffering

    // For now, just log receipt
    UE_LOG(LogTemp, VeryVerbose, TEXT("[StaticWaves] Received %d bytes of audio"), Size);
}

void UStaticWavesMusicSubsystem::Tick(float DeltaTime)
{
    // Handle smooth context transitions
    if (TransitionAlpha < 1.0f)
    {
        TransitionAlpha += DeltaTime / TransitionDuration;
        TransitionAlpha = FMath::Clamp(TransitionAlpha, 0.0f, 1.0f);

        // Lerp all context values
        CurrentContext.Energy = FMath::Lerp(CurrentContext.Energy, TargetContext.Energy, TransitionAlpha);
        CurrentContext.Tension = FMath::Lerp(CurrentContext.Tension, TargetContext.Tension, TransitionAlpha);
        CurrentContext.Darkness = FMath::Lerp(CurrentContext.Darkness, TargetContext.Darkness, TransitionAlpha);
        CurrentContext.Complexity = FMath::Lerp(CurrentContext.Complexity, TargetContext.Complexity, TransitionAlpha);

        // Send update
        SendControlUpdate();
    }

    return true; // Continue ticking
}
