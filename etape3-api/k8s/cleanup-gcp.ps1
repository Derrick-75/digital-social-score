# Script de Nettoyage GCP pour Digital Social Score API
# Suppression sécurisée des ressources GCP

param(
    [string]$ProjectId = "",
    [string]$ClusterName = "dss-cluster",
    [string]$Zone = "europe-west1-b",
    [switch]$DeleteCluster = $false,
    [switch]$DeleteImages = $false,
    [switch]$Force = $false
)

Write-Host "🧹 Nettoyage des ressources GCP - Digital Social Score" -ForegroundColor Yellow
Write-Host "======================================================" -ForegroundColor Yellow

# Fonction de confirmation
function Confirm-Action {
    param([string]$Message)
    
    if ($Force) {
        return $true
    }
    
    Write-Host "$Message" -ForegroundColor Yellow
    $response = Read-Host "Confirmez-vous? (y/N)"
    return ($response -eq "y" -or $response -eq "Y")
}

# Vérification des prérequis
$currentProject = gcloud config get-value project 2>$null
if (-not $currentProject) {
    Write-Host "❌ Aucun projet GCP configuré" -ForegroundColor Red
    exit 1
}

if ($ProjectId -and $currentProject -ne $ProjectId) {
    gcloud config set project $ProjectId
    $currentProject = $ProjectId
}

Write-Host "🔧 Projet GCP: $currentProject" -ForegroundColor Cyan

# 1. Nettoyage des ressources Kubernetes
Write-Host "`n1️⃣ Nettoyage des ressources Kubernetes..." -ForegroundColor Green

$context = kubectl config current-context 2>$null
if ($context -and $context -match "gke_") {
    Write-Host "Contexte kubectl: $context" -ForegroundColor Blue
    
    # Vérification du namespace
    $namespace = kubectl get namespace digital-social-score 2>$null
    if ($LASTEXITCODE -eq 0) {
        if (Confirm-Action "Supprimer toutes les ressources dans le namespace 'digital-social-score'?") {
            Write-Host "Suppression des ressources Kubernetes..." -ForegroundColor Blue
            
            # Suppression des ressources spécifiques dans l'ordre
            kubectl delete hpa --all -n digital-social-score 2>$null
            kubectl delete ingress --all -n digital-social-score 2>$null
            kubectl delete services --all -n digital-social-score 2>$null
            kubectl delete deployments --all -n digital-social-score 2>$null
            kubectl delete configmaps --all -n digital-social-score 2>$null
            kubectl delete secrets --all -n digital-social-score 2>$null
            
            # Suppression du namespace
            kubectl delete namespace digital-social-score 2>$null
            
            Write-Host "✅ Ressources Kubernetes supprimées" -ForegroundColor Green
        } else {
            Write-Host "⏭️ Suppression des ressources Kubernetes ignorée" -ForegroundColor Gray
        }
    } else {
        Write-Host "ℹ️ Namespace 'digital-social-score' non trouvé" -ForegroundColor Gray
    }
} else {
    Write-Host "ℹ️ Aucun contexte GKE actif" -ForegroundColor Gray
}

# 2. Nettoyage des images Docker dans GCR
Write-Host "`n2️⃣ Nettoyage des images Docker..." -ForegroundColor Green

if ($DeleteImages) {
    $imageName = "gcr.io/$currentProject/digital-social-score"
    
    # Liste des images
    $images = gcloud container images list-tags $imageName --format="value(digest)" 2>$null
    if ($images -and $LASTEXITCODE -eq 0) {
        if (Confirm-Action "Supprimer toutes les images Docker de $imageName`?") {
            Write-Host "Suppression des images Docker..." -ForegroundColor Blue
            
            foreach ($digest in $images) {
                if ($digest) {
                    gcloud container images delete "$imageName@$digest" --quiet --force-delete-tags 2>$null
                }
            }
            
            Write-Host "✅ Images Docker supprimées" -ForegroundColor Green
        } else {
            Write-Host "⏭️ Suppression des images Docker ignorée" -ForegroundColor Gray
        }
    } else {
        Write-Host "ℹ️ Aucune image trouvée pour $imageName" -ForegroundColor Gray
    }
} else {
    Write-Host "⏭️ Suppression des images Docker ignorée (utilisez -DeleteImages)" -ForegroundColor Gray
}

# 3. Suppression des adresses IP statiques
Write-Host "`n3️⃣ Nettoyage des adresses IP statiques..." -ForegroundColor Green

$staticIPs = gcloud compute addresses list --filter="name:dss-api-ip" --format="value(name)" 2>$null
if ($staticIPs -and $LASTEXITCODE -eq 0) {
    if (Confirm-Action "Supprimer les adresses IP statiques?") {
        Write-Host "Suppression des adresses IP statiques..." -ForegroundColor Blue
        
        foreach ($ip in $staticIPs) {
            if ($ip) {
                gcloud compute addresses delete $ip --global --quiet 2>$null
            }
        }
        
        Write-Host "✅ Adresses IP statiques supprimées" -ForegroundColor Green
    } else {
        Write-Host "⏭️ Suppression des adresses IP statiques ignorée" -ForegroundColor Gray
    }
} else {
    Write-Host "ℹ️ Aucune adresse IP statique trouvée" -ForegroundColor Gray
}

# 4. Suppression des certificats SSL managés
Write-Host "`n4️⃣ Nettoyage des certificats SSL managés..." -ForegroundColor Green

$certificates = gcloud compute ssl-certificates list --filter="name:dss-api-ssl-cert" --format="value(name)" 2>$null
if ($certificates -and $LASTEXITCODE -eq 0) {
    if (Confirm-Action "Supprimer les certificats SSL managés?") {
        Write-Host "Suppression des certificats SSL..." -ForegroundColor Blue
        
        foreach ($cert in $certificates) {
            if ($cert) {
                gcloud compute ssl-certificates delete $cert --quiet 2>$null
            }
        }
        
        Write-Host "✅ Certificats SSL supprimés" -ForegroundColor Green
    } else {
        Write-Host "⏭️ Suppression des certificats SSL ignorée" -ForegroundColor Gray
    }
} else {
    Write-Host "ℹ️ Aucun certificat SSL managé trouvé" -ForegroundColor Gray
}

# 5. Suppression du cluster GKE
Write-Host "`n5️⃣ Suppression du cluster GKE..." -ForegroundColor Green

if ($DeleteCluster) {
    $clusterExists = gcloud container clusters describe $ClusterName --zone=$Zone 2>$null
    if ($LASTEXITCODE -eq 0) {
        if (Confirm-Action "ATTENTION: Supprimer complètement le cluster GKE '$ClusterName'? Cette action est irréversible!") {
            Write-Host "Suppression du cluster GKE (cela peut prendre plusieurs minutes)..." -ForegroundColor Blue
            
            gcloud container clusters delete $ClusterName --zone=$Zone --quiet
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ Cluster GKE supprimé" -ForegroundColor Green
            } else {
                Write-Host "❌ Erreur lors de la suppression du cluster" -ForegroundColor Red
            }
        } else {
            Write-Host "⏭️ Suppression du cluster GKE ignorée" -ForegroundColor Gray
        }
    } else {
        Write-Host "ℹ️ Cluster '$ClusterName' non trouvé dans la zone $Zone" -ForegroundColor Gray
    }
} else {
    Write-Host "⏭️ Suppression du cluster GKE ignorée (utilisez -DeleteCluster)" -ForegroundColor Gray
    Write-Host "ℹ️ Le cluster sera toujours facturé tant qu'il existe" -ForegroundColor Yellow
}

# 6. Nettoyage des configurations locales
Write-Host "`n6️⃣ Nettoyage des configurations locales..." -ForegroundColor Green

if ($DeleteCluster -and (Confirm-Action "Nettoyer la configuration kubectl locale?")) {
    Write-Host "Nettoyage de la configuration kubectl..." -ForegroundColor Blue
    
    # Suppression du contexte kubectl
    $context = "gke_$currentProject`_$Zone`_$ClusterName"
    kubectl config delete-context $context 2>$null
    kubectl config delete-cluster $context 2>$null
    
    Write-Host "✅ Configuration kubectl nettoyée" -ForegroundColor Green
} else {
    Write-Host "⏭️ Configuration kubectl conservée" -ForegroundColor Gray
}

# 7. Résumé des coûts évités
Write-Host "`n💰 Estimation des coûts évités:" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

if ($DeleteCluster) {
    Write-Host "✅ Cluster GKE: ~$60-120/mois (selon la configuration)" -ForegroundColor Green
} else {
    Write-Host "⚠️ Cluster GKE: ~$60-120/mois (toujours actif)" -ForegroundColor Yellow
}

if ($DeleteImages) {
    Write-Host "✅ Images Docker: ~$0.10/Go/mois (économisé)" -ForegroundColor Green
} else {
    Write-Host "ℹ️ Images Docker: ~$0.10/Go/mois (conservées)" -ForegroundColor Blue
}

Write-Host "✅ Adresses IP statiques: ~$1.46/IP/mois (économisé)" -ForegroundColor Green
Write-Host "✅ Certificats SSL managés: Gratuits (nettoyés)" -ForegroundColor Green

# 8. Recommandations finales
Write-Host "`n📋 Recommandations:" -ForegroundColor Cyan
Write-Host "===================" -ForegroundColor Cyan

if (-not $DeleteCluster) {
    Write-Host "⚠️ Le cluster GKE est toujours actif et facturé" -ForegroundColor Yellow
    Write-Host "   Pour le supprimer: .\cleanup-gcp.ps1 -DeleteCluster" -ForegroundColor White
}

if (-not $DeleteImages) {
    Write-Host "ℹ️ Les images Docker sont conservées dans GCR" -ForegroundColor Blue
    Write-Host "   Pour les supprimer: .\cleanup-gcp.ps1 -DeleteImages" -ForegroundColor White
}

Write-Host "`n📊 Vérification des ressources restantes:" -ForegroundColor Yellow
Write-Host "===========================================" -ForegroundColor Yellow

Write-Host "`n🔍 Clusters GKE:" -ForegroundColor Blue
gcloud container clusters list 2>$null

Write-Host "`n🔍 Images Docker:" -ForegroundColor Blue
gcloud container images list --repository=gcr.io/$currentProject 2>$null

Write-Host "`n🔍 Adresses IP:" -ForegroundColor Blue
gcloud compute addresses list --filter="name:dss*" 2>$null

Write-Host "`n🔍 Certificats SSL:" -ForegroundColor Blue
gcloud compute ssl-certificates list --filter="name:dss*" 2>$null

Write-Host "`n✅ Nettoyage terminé!" -ForegroundColor Green
Write-Host "=====================" -ForegroundColor Green

if ($DeleteCluster) {
    Write-Host "🎉 Toutes les ressources principales ont été supprimées" -ForegroundColor Green
    Write-Host "💸 Les coûts GCP pour ce projet sont maintenant minimaux" -ForegroundColor Green
} else {
    Write-Host "⚠️ Le cluster GKE est toujours actif" -ForegroundColor Yellow
    Write-Host "💡 Utilisez -DeleteCluster pour supprimer complètement le cluster" -ForegroundColor Cyan
}

Write-Host "`n📚 Commandes de vérification:" -ForegroundColor Yellow
Write-Host "gcloud projects get-iam-policy $currentProject" -ForegroundColor White
Write-Host "gcloud billing accounts projects list" -ForegroundColor White
Write-Host "gcloud compute instances list" -ForegroundColor White
