#get custom data from php-fpm and nginx status pages
import requests
import boto3

def get_fpm_metrics(version:str, url:str)->dict:
    print('\n--> PHP_FPM status requested <--')
    payload = {} 
    response = requests.get(url)
    #print(response.text)
    relevant = ['acceptedconn', 'listenqueue','idleprocesses','activeprocesses',]
    for line in response.text.split('\n'):
        try:
            data_cleaned = []
            data_cleaned = line.replace(' ','').split(':')
            #print(data_cleaned[0]+ ': '+data_cleaned[1])
            if data_cleaned[0] in relevant:
                payload[data_cleaned[0]] = int(data_cleaned[1])
        except:
            print('error en la linea:', line)
    print(payload)
    for item in payload:
        publish_custom_metric('php',version, item, payload[item])
    return payload

def get_nginx_metrics(version:str, url:str)->dict:
    print('\n--> NGINX status requested <--')
    response = requests.get(url)
    data_cleaned = []
    payload = {}
    #for line in response.text.split('\n'):
    raw_data = response.text.split('\n')
    if 'connections' in raw_data[0]:
        data_cleaned = raw_data[0].replace(' ','').split(':')
        payload[data_cleaned[0].lower()] = int(data_cleaned[1])

    cleaned = raw_data[2].split(' ')
    payload['server'] = int(cleaned[1])
    payload['accepts'] = int(cleaned[2])
    payload['handledrequest'] = int(cleaned[3])
    if 'Reading' in raw_data[3]:
        data_cleaned = []
        data_cleaned = raw_data[3].lower().replace(' ','').split('w')
        #for item in data_cleaned:
        payload['reading'] = int(data_cleaned[0].split(':')[1])
        payload['writing'] = int(data_cleaned[1].split(':')[1])
        payload['waiting'] = int(data_cleaned[2].split(':')[1])
    print(payload)

    for item in payload:
        publish_custom_metric('nginx', version, item, payload[item])
    return payload

def publish_custom_metric(service:str, version:str, name:str, data:int)->bool:
    try:
        CloudWatch = boto3.client('cloudwatch')
        print(f'Service: {service}')
        print(f'Version: {version}')
        print(f'Sending metric: {name} -> {data}')
        response = CloudWatch.put_metric_data(
        MetricData = [
            {
                'MetricName': name,
                'Unit': 'Count',
                'Value': data,
                'Dimensions': [
                    {
                        'Name': 'InstanceId',
                        'Value': 'i-050a16f1dec54a4d1'
                    },
                    {
                        'Name': 'version',
                        'Value': version 
                    },
                    {
                        'Name': 'service',
                        'Value': service 
                    }
                ],
            },
        ],
        Namespace='Custom_metrics'
        )
    except:
        print('Error publicando metric: ', name)

def read_config(file:str) -> list:
    try:
        urls = []
        with open(file, 'r') as fd:
            for line in fd:
                if '#' not in line and line != '\n':
                    urls.append(line.split(';'))
        return urls
    except:
        print('Error leyendo archivo de configuracion')

if __name__ == "__main__":
    urls = read_config('/app/urls.conf')
    for url in urls:
        if url[0] == 'fpm':
            get_fpm_metrics(str(url[1]).strip(),str(url[2]).strip())
        elif url[0] == 'nginx':
            get_nginx_metrics(str(url[1]).strip(),str(url[2]).strip())
