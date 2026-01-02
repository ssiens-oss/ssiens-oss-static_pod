/**
 * StaticWaves Music Subsystem for Unreal Engine
 * Real-time adaptive music integration
 *
 * Copyright StaticWaves 2026
 */

#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "WebSocketsModule.h"
#include "IWebSocket.h"
#include "StaticWavesMusicSubsystem.generated.h"

/**
 * Music context structure
 * Controls the adaptive music state
 */
USTRUCT(BlueprintType)
struct FMusicContext
{
    GENERATED_BODY()

    /** Energy level: 0 = calm, 1 = energetic */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Music", meta = (ClampMin = "0.0", ClampMax = "1.0"))
    float Energy = 0.5f;

    /** Tension level: 0 = relaxed, 1 = intense */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Music", meta = (ClampMin = "0.0", ClampMax = "1.0"))
    float Tension = 0.5f;

    /** Darkness: 0 = bright, 1 = dark */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Music", meta = (ClampMin = "0.0", ClampMax = "1.0"))
    float Darkness = 0.5f;

    /** Complexity: 0 = simple, 1 = complex */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Music", meta = (ClampMin = "0.0", ClampMax = "1.0"))
    float Complexity = 0.5f;

    FMusicContext()
        : Energy(0.5f), Tension(0.5f), Darkness(0.5f), Complexity(0.5f)
    {
    }

    FString ToJson() const
    {
        return FString::Printf(TEXT("{\"energy\":%.2f,\"tension\":%.2f,\"darkness\":%.2f,\"complexity\":%.2f}"),
            Energy, Tension, Darkness, Complexity);
    }
};

/**
 * StaticWaves Music Subsystem
 * Manages adaptive music state and WebSocket connection
 */
UCLASS()
class STATICWAVES_API UStaticWavesMusicSubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    UStaticWavesMusicSubsystem();

    //~ Begin USubsystem Interface
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;
    //~ End USubsystem Interface

    /**
     * Connect to StaticWaves server
     * @param ServerURL WebSocket server URL (default: ws://localhost:8765)
     */
    UFUNCTION(BlueprintCallable, Category = "StaticWaves")
    void Connect(const FString& ServerURL = TEXT("ws://localhost:8765"));

    /**
     * Disconnect from server
     */
    UFUNCTION(BlueprintCallable, Category = "StaticWaves")
    void Disconnect();

    /**
     * Check if connected to server
     */
    UFUNCTION(BlueprintPure, Category = "StaticWaves")
    bool IsConnected() const { return bIsConnected; }

    /**
     * Set music context immediately
     */
    UFUNCTION(BlueprintCallable, Category = "StaticWaves")
    void SetMusicContext(FMusicContext Context);

    /**
     * Transition to new context smoothly
     * @param Context Target context
     * @param TransitionTime Time in seconds to reach target
     */
    UFUNCTION(BlueprintCallable, Category = "StaticWaves")
    void TransitionToContext(FMusicContext Context, float TransitionTime = 1.0f);

    /**
     * Get current music context
     */
    UFUNCTION(BlueprintPure, Category = "StaticWaves")
    FMusicContext GetCurrentContext() const { return CurrentContext; }

    //
    // Quick Presets
    //

    UFUNCTION(BlueprintCallable, Category = "StaticWaves|Presets")
    void SetExploration();

    UFUNCTION(BlueprintCallable, Category = "StaticWaves|Presets")
    void SetCombat();

    UFUNCTION(BlueprintCallable, Category = "StaticWaves|Presets")
    void SetBoss();

    UFUNCTION(BlueprintCallable, Category = "StaticWaves|Presets")
    void SetPuzzle();

    UFUNCTION(BlueprintCallable, Category = "StaticWaves|Presets")
    void SetVictory();

    /**
     * Push a music event (generic way to affect music)
     * @param EventName Event identifier
     * @param Intensity Event intensity (0-1)
     */
    UFUNCTION(BlueprintCallable, Category = "StaticWaves")
    void PushMusicEvent(FName EventName, float Intensity = 1.0f);

protected:
    /** WebSocket connection */
    TSharedPtr<IWebSocket> WebSocket;

    /** Current music context */
    UPROPERTY(BlueprintReadOnly, Category = "StaticWaves")
    FMusicContext CurrentContext;

    /** Target context for smooth transitions */
    FMusicContext TargetContext;

    /** Transition progress */
    float TransitionAlpha = 1.0f;

    /** Transition duration */
    float TransitionDuration = 1.0f;

    /** Connection state */
    bool bIsConnected = false;

    /** Server URL */
    FString ServerURL;

private:
    /** Send control update to server */
    void SendControlUpdate();

    /** Handle WebSocket connected */
    void OnConnected();

    /** Handle WebSocket connection error */
    void OnConnectionError(const FString& Error);

    /** Handle WebSocket closed */
    void OnClosed(int32 StatusCode, const FString& Reason, bool bWasClean);

    /** Handle WebSocket message received */
    void OnMessage(const FString& Message);

    /** Handle WebSocket binary message */
    void OnRawMessage(const void* Data, SIZE_T Size, SIZE_T BytesRemaining);

    /** Tick function for smooth transitions */
    void Tick(float DeltaTime);

    /** Delegate handle for ticker */
    FTSTicker::FDelegateHandle TickerHandle;
};
