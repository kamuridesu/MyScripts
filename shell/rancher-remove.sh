#!/bin/bash

# Define Rancher-related namespaces
NAMESPACES=("cattle-system" "cattle-impersonation-system" "cattle-fleet-system")

# Delete all resources in each namespace
for NAMESPACE in "${NAMESPACES[@]}"; do
  echo "Deleting all resources in namespace: $NAMESPACE"
  kubectl delete all --all -n $NAMESPACE
done

# Remove Rancher webhook configurations
echo "Removing Rancher webhook configurations..."
kubectl get validatingwebhookconfigurations | grep 'rancher' | awk '{print $1}' | xargs kubectl delete validatingwebhookconfiguration
kubectl get mutatingwebhookconfigurations | grep 'rancher' | awk '{print $1}' | xargs kubectl delete mutatingwebhookconfiguration

# Delete Rancher-related namespaces
for NAMESPACE in "${NAMESPACES[@]}"; do
  echo "Deleting namespace: $NAMESPACE"
  kubectl delete namespace $NAMESPACE
done

# Handle stuck namespaces by removing finalizers
for NAMESPACE in "${NAMESPACES[@]}"; do
  if kubectl get namespace $NAMESPACE -o jsonpath='{.status.phase}' | grep -q 'Terminating'; then
    echo "Namespace $NAMESPACE is stuck in Terminating state. Removing finalizers..."
    kubectl get namespace $NAMESPACE -o json | jq '.spec.finalizers=[]' > temp-$NAMESPACE.json
    kubectl replace --raw "/api/v1/namespaces/$NAMESPACE/finalize" -f temp-$NAMESPACE.json
    rm temp-$NAMESPACE.json
  fi
done

echo "Rancher removal process is complete. Verify the cleanup to ensure no Rancher-related resources remain."

