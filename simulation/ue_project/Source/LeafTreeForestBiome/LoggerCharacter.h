#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "InputActionValue.h"
#include "LoggerCharacter.generated.h"

class UInputMappingContext;
class UInputAction;
class USpringArmComponent;
class UCameraComponent;
class UStaticMeshComponent;
class UAnimMontage;

UCLASS(Blueprintable)
class LEAFTREEFORESTBIOME_API ALoggerCharacter : public ACharacter
{
    GENERATED_BODY()

public:
    ALoggerCharacter();

    // --- PUBLIC COMPONENTS ---
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Components", meta = (AllowPrivateAccess = "true"))
    UStaticMeshComponent* AxeMesh;

    // --- BONE & SOCKET NAMES ---
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Bone Names")
    FName RightHandBone;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Bone Names")
    FName LeftHandSocket;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Bone Names")
    FName RightHandGripSocketName;

    // --- WEAPON GETTER ---
    // Works just like "Get Current Weapon" in shooter games
    UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Weapon")
    UStaticMeshComponent* GetAxeMesh() const;

    // --- IK HELPER ---
    UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Animation|IK")
    FTransform GetRightHandIKTransform() const;

    virtual void SetupPlayerInputComponent(class UInputComponent* PlayerInputComponent) override;
    virtual void OnConstruction(const FTransform& Transform) override;

protected:
    virtual void BeginPlay() override;

    // --- INPUT ACTIONS ---
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
    UInputMappingContext* DefaultMappingContext;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
    UInputAction* MoveAction;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
    UInputAction* LookAction;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
    UInputAction* ChopAction;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Animation")
    UAnimMontage* ChopMontage;

    void Move(const FInputActionValue& Value);
    void Look(const FInputActionValue& Value);
    void Chop(const FInputActionValue& Value);

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Camera")
    USpringArmComponent* CameraBoom;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Camera")
    UCameraComponent* FollowCamera;

private:
    void ApplyHeightBasedScaling();
};