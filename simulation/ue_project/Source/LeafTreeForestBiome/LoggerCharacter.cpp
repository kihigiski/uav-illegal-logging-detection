#include "LoggerCharacter.h"
#include "EnhancedInputComponent.h"
#include "EnhancedInputSubsystems.h"
#include "GameFramework/SpringArmComponent.h"
#include "Camera/CameraComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Animation/AnimMontage.h"
#include "Engine/StaticMesh.h"
#include "Engine/SkeletalMesh.h"

ALoggerCharacter::ALoggerCharacter()
{
    PrimaryActorTick.bCanEverTick = true;

    // Default Movement Config
    GetCharacterMovement()->bOrientRotationToMovement = true;

    // Components
    CameraBoom = CreateDefaultSubobject<USpringArmComponent>(TEXT("CameraBoom"));
    CameraBoom->SetupAttachment(RootComponent);
    CameraBoom->bUsePawnControlRotation = true;

    FollowCamera = CreateDefaultSubobject<UCameraComponent>(TEXT("FollowCamera"));
    FollowCamera->SetupAttachment(CameraBoom, USpringArmComponent::SocketName);

    // Variable Defaults
    RightHandBone = FName("RightHand");
    LeftHandSocket = FName("hand_leSocket");
    RightHandGripSocketName = FName("RightHandGrip");

    AxeMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("AxeMesh"));

    // Attachment: Ensure the Axe is linked to the Mesh immediately
    if (GetMesh())
    {
        AxeMesh->SetupAttachment(GetMesh(), LeftHandSocket);
    }
}

void ALoggerCharacter::OnConstruction(const FTransform& Transform)
{
    Super::OnConstruction(Transform);

    // Keep attachment synced in the editor
    if (GetMesh() && AxeMesh)
    {
        AxeMesh->AttachToComponent(GetMesh(), FAttachmentTransformRules::KeepRelativeTransform, LeftHandSocket);
    }

    ApplyHeightBasedScaling();
}

// --- WEAPON GETTER IMPLEMENTATION ---
UStaticMeshComponent* ALoggerCharacter::GetAxeMesh() const
{
    return AxeMesh;
}

FTransform ALoggerCharacter::GetRightHandIKTransform() const
{
    // Safety check: If things are missing, return a safe "Hand at Shoulder" location
    // to prevent the arm from snapping to the character's feet (0,0,0)
    if (!AxeMesh || !GetMesh() || !AxeMesh->GetStaticMesh() || !AxeMesh->DoesSocketExist(RightHandGripSocketName))
    {
        return GetMesh()->GetSocketTransform(RightHandBone, RTS_Component);
    }

    // 1. Get the World Transform of the socket on the Axe
    FTransform WorldTransform = AxeMesh->GetSocketTransform(RightHandGripSocketName, ERelativeTransformSpace::RTS_World);

    // 2. Convert to Component Space so the AnimGraph can use it directly
    return WorldTransform.GetRelativeTransform(GetMesh()->GetComponentTransform());
}

void ALoggerCharacter::BeginPlay()
{
    Super::BeginPlay();
}

void ALoggerCharacter::ApplyHeightBasedScaling()
{
    if (!GetMesh() || !AxeMesh || !GetMesh()->SkeletalMesh || !AxeMesh->GetStaticMesh()) return;

    FBoxSphereBounds BodyBounds = GetMesh()->CalcBounds(GetMesh()->GetComponentTransform());
    float CharacterHeight = BodyBounds.BoxExtent.Z * 2.0f;

    float TargetHandleLengthCM = (CharacterHeight < 172.0f) ? 55.0f : (CharacterHeight <= 180.0f ? 65.0f : 83.8f);

    FBoxSphereBounds AxeBounds = AxeMesh->GetStaticMesh()->GetBounds();
    float RawMeshSize = FMath::Max3(AxeBounds.BoxExtent.X, AxeBounds.BoxExtent.Y, AxeBounds.BoxExtent.Z) * 2.0f;

    if (RawMeshSize > 0.1f)
    {
        float FinalScale = TargetHandleLengthCM / RawMeshSize;
        AxeMesh->SetRelativeScale3D(FVector(FinalScale));

        
    }
}

void ALoggerCharacter::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
    Super::SetupPlayerInputComponent(PlayerInputComponent);

    // 1. Load the Mapping Context so the game knows what keys to listen for
    if (APlayerController* PlayerController = Cast<APlayerController>(GetController()))
    {
        if (UEnhancedInputLocalPlayerSubsystem* Subsystem = ULocalPlayer::GetSubsystem<UEnhancedInputLocalPlayerSubsystem>(PlayerController->GetLocalPlayer()))
        {
            if (DefaultMappingContext)
            {
                Subsystem->AddMappingContext(DefaultMappingContext, 0);
            }
        }
    }

    // 2. Bind the Actions to the Functions
    if (UEnhancedInputComponent* EnhancedInputComponent = CastChecked<UEnhancedInputComponent>(PlayerInputComponent))
    {
        EnhancedInputComponent->BindAction(MoveAction, ETriggerEvent::Triggered, this, &ALoggerCharacter::Move);
        EnhancedInputComponent->BindAction(LookAction, ETriggerEvent::Triggered, this, &ALoggerCharacter::Look);
        EnhancedInputComponent->BindAction(ChopAction, ETriggerEvent::Started, this, &ALoggerCharacter::Chop);
    }
}

// --- INPUT IMPLEMENTATIONS ---

void ALoggerCharacter::Move(const FInputActionValue& Value)
{
    FVector2D MovementVector = Value.Get<FVector2D>();

    if (Controller != nullptr)
    {
        // Find out which way is forward
        const FRotator Rotation = Controller->GetControlRotation();
        const FRotator YawRotation(0, Rotation.Yaw, 0);

        // Get forward vector
        const FVector ForwardDirection = FRotationMatrix(YawRotation).GetUnitAxis(EAxis::X);
        // Get right vector 
        const FVector RightDirection = FRotationMatrix(YawRotation).GetUnitAxis(EAxis::Y);

        // Add movement 
        AddMovementInput(ForwardDirection, MovementVector.Y);
        AddMovementInput(RightDirection, MovementVector.X);
    }
}

void ALoggerCharacter::Look(const FInputActionValue& Value)
{
    FVector2D LookAxisVector = Value.Get<FVector2D>();

    if (Controller != nullptr)
    {
        // Add yaw and pitch input to controller
        AddControllerYawInput(LookAxisVector.X);
        AddControllerPitchInput(LookAxisVector.Y);
    }
}

void ALoggerCharacter::Chop(const FInputActionValue& Value)
{
    if (ChopMontage)
    {
        PlayAnimMontage(ChopMontage);
    }
}