NAMESPACE=$1
LOGS_FOLDER=$HOME/documents/logs/$NAMESPACE
mkdir -p $LOGS_FOLDER

OLD_IFS=$IFS
get_logs() {
    IFS=$'\n'
    for POD in $(kubectl get pods -n $NAMESPACE | tail -n +2); do
        echo "Coletando logs e métricas do pod $POD_NAME"
        # tail=-1 pega todos os logs do pod, mas não todos os logs
        # o Kubernetes faz uma rotação de logs quando o arquivo atinge um tamanho x
        # logo nao conseguimos pegar todos os logs desde o início em pods rodando a muito tempo
        POD_NAME=$(echo $POD | awk '{print $1}');
        RESTARTS=$(echo $POD | awk '{print $4}');
        kubectl logs --tail=-1 -n $NAMESPACE $POD_NAME > "$LOGS_FOLDER/$POD_NAME.log"
        if [[ $? -ne 0 ]]; then
            echo "Erro! Falha ao salvar os logs!"
            exit 1;
        fi
        kubectl top pod -n $NAMESPACE $POD_NAME --containers > "$LOGS_FOLDER/$POD_NAME.metrics.log"
        echo "Restarts: $RESTARTS" >> "$LOGS_FOLDER/$POD_NAME.metrics.log"
        if [[ $? -ne 0 ]]; then
            echo "Erro! Falha ao salvar as métricas!"
            exit 1;
        fi
    done
    IFS=$OLD_IFS
}

restart() {
    for DEPLOYMENT in $(kubectl get deployment -n $NAMESPACE | awk '{print $1}' | tail -n +2); do
        echo "Reiniciando deployment $DEPLOYMENT"
        kubectl rollout restart deployment $DEPLOYMENT -n $NAMESPACE;
        if [[ $? -ne 0 ]]; then
            echo "Erro! Falha ao reiniciar os pods!"
            exit 1;
        fi
    done
}

get_logs
restart

echo "Reinciado com sucesso! Salvo em $LOGS_FOLDER";
