import csv
import multiprocessing
import os
from django.http import JsonResponse
from util.CustomJSONEncoder import CustomJsonEncoder
from util.codes import normal_code, system_error_code
import json
from pathlib import Path
import paramiko
import subprocess
from hdfs import InsecureClient
from pyspark import SparkConf
import pymysql
from pyspark.sql import SparkSession

from util.configread import config_read

parent_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
hadoop_client = InsecureClient('http://localhost:9870',user="hadoop")
dbtype, host, port, user, passwd, dbName, charset, hasHadoop = config_read(os.path.join(parent_directory,"config.ini"))
master_host = "localhost"
spark_dir = "D:/spark312"
python_dir = "D:/biye/python37"

def upload_csv():
    mysql_conn = pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=passwd,
        database=dbName.replace(" ", "").strip()
    )
    cursor = mysql_conn.cursor()
    cursor.execute("SELECT * FROM T_Core_attractions")
    ctripjd_column_info = cursor.fetchall()
    # 将数据写入 CSV 文件
    ctripjd_path = os.path.join(parent_directory, "ctripjd.csv")
    with open(ctripjd_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        # 写入表头
        writer.writerow([desc[0] for desc in cursor.description])
        # 写入数据行
        for row in ctripjd_column_info:
            writer.writerow(row)
    # 上传映射文件
    ctripjd_hdfs_csv_path = f'/input/ctripjd.csv'
    ctripjd_local_csv_path = os.path.join(parent_directory,"ctripjd.csv")
    # 删除已有的数据
    if hadoop_client.status(ctripjd_hdfs_csv_path, strict=False):
        hadoop_client.delete(ctripjd_hdfs_csv_path, recursive=True)
    hadoop_client.upload(ctripjd_hdfs_csv_path, ctripjd_local_csv_path)
    cursor.execute("SELECT * FROM T_Attraction_Reviews")
    ctrippinglun_column_info = cursor.fetchall()
    # 将数据写入 CSV 文件
    ctrippinglun_path = os.path.join(parent_directory, "ctrippinglun.csv")
    with open(ctrippinglun_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        # 写入表头
        writer.writerow([desc[0] for desc in cursor.description])
        # 写入数据行
        for row in ctrippinglun_column_info:
            writer.writerow(row)
    # 上传映射文件
    ctrippinglun_hdfs_csv_path = f'/input/ctrippinglun.csv'
    ctrippinglun_local_csv_path = os.path.join(parent_directory,"ctrippinglun.csv")
    # 删除已有的数据
    if hadoop_client.status(ctrippinglun_hdfs_csv_path, strict=False):
        hadoop_client.delete(ctrippinglun_hdfs_csv_path, recursive=True)
    hadoop_client.upload(ctrippinglun_hdfs_csv_path, ctrippinglun_local_csv_path)
    cursor.execute("SELECT * FROM T_Sentiment_Analysis")
    qingganfenxi_column_info = cursor.fetchall()
    # 将数据写入 CSV 文件
    qingganfenxi_path = os.path.join(parent_directory, "qingganfenxi.csv")
    with open(qingganfenxi_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        # 写入表头
        writer.writerow([desc[0] for desc in cursor.description])
        # 写入数据行
        for row in qingganfenxi_column_info:
            writer.writerow(row)
    # 上传映射文件
    qingganfenxi_hdfs_csv_path = f'/input/qingganfenxi.csv'
    qingganfenxi_local_csv_path = os.path.join(parent_directory,"qingganfenxi.csv")
    # 删除已有的数据
    if hadoop_client.status(qingganfenxi_hdfs_csv_path, strict=False):
        hadoop_client.delete(qingganfenxi_hdfs_csv_path, recursive=True)
    hadoop_client.upload(qingganfenxi_hdfs_csv_path, qingganfenxi_local_csv_path)
    # 上传group文件
    group_path = f'/input/spark_group.py'
    localgroup_path = os.path.join(parent_directory,"main","spark_group.py")
    # 删除已有的数据
    if not hadoop_client.status(group_path, strict=False):
        hadoop_client.upload(group_path, localgroup_path)
    # 上传value文件
    value_path = f'/input/spark_value.py'
    localvalue_path = os.path.join(parent_directory,"main","spark_value.py")
    # 删除已有的数据
    if not hadoop_client.status(value_path, strict=False):
        hadoop_client.upload(value_path, localvalue_path)

    cursor.close()
    mysql_conn.close()

# 执行分析命令
def send_cmd():

    job_commands = [
    f'''{spark_dir}/bin/spark-submit.cmd \
        --master spark://{master_host}:7077 \
        --conf "spark.pyspark.driver.python={python_dir}/python.exe" \
        --conf "spark.pyspark.python={python_dir}/python.exe" \
        hdfs://localhost:9000/input/spark_group.py \
        ctripjd--districtname
    ''',
    f'''{spark_dir}/bin/spark-submit.cmd \
        --master spark://{master_host}:7077 \
        --conf "spark.pyspark.driver.python={python_dir}/python.exe" \
        --conf "spark.pyspark.python={python_dir}/python.exe" \
        hdfs://localhost:9000/input/spark_group.py \
        ctrippinglun--content
    ''',
    f'''{spark_dir}/bin/spark-submit.cmd \
        --master spark://{master_host}:7077 \
        --conf "spark.pyspark.driver.python={python_dir}/python.exe" \
        --conf "spark.pyspark.python={python_dir}/python.exe" \
        hdfs://localhost:9000/input/spark_group.py \
        qingganfenxi--fenxijieguo
    ''',
    f'''{spark_dir}/bin/spark-submit.cmd \
        --master spark://{master_host}:7077 \
        --conf "spark.pyspark.driver.python={python_dir}/python.exe" \
        --conf "spark.pyspark.python={python_dir}/python.exe" \
        hdfs://localhost:9000/input/spark_value.py \
        ctripjd--poiname--commentscore--
    ''',
    f'''{spark_dir}/bin/spark-submit.cmd \
        --master spark://{master_host}:7077 \
        --conf "spark.pyspark.driver.python={python_dir}/python.exe" \
        --conf "spark.pyspark.python={python_dir}/python.exe" \
        hdfs://localhost:9000/input/spark_value.py \
        ctripjd--poiname--commentcount--
    ''',
    f'''{spark_dir}/bin/spark-submit.cmd \
        --master spark://{master_host}:7077 \
        --conf "spark.pyspark.driver.python={python_dir}/python.exe" \
        --conf "spark.pyspark.python={python_dir}/python.exe" \
        hdfs://localhost:9000/input/spark_value.py \
        ctripjd--poiname--heatscore--
    ''',
    f'''{spark_dir}/bin/spark-submit.cmd \
        --master spark://{master_host}:7077 \
        --conf "spark.pyspark.driver.python={python_dir}/python.exe" \
        --conf "spark.pyspark.python={python_dir}/python.exe" \
        hdfs://localhost:9000/input/spark_value.py \
        ctripjd--poiname--jiage--
    ''',
    f'''{spark_dir}/bin/spark-submit.cmd \
        --master spark://{master_host}:7077 \
        --conf "spark.pyspark.driver.python={python_dir}/python.exe" \
        --conf "spark.pyspark.python={python_dir}/python.exe" \
        hdfs://localhost:9000/input/spark_value.py \
        ctripjd--poiname--storeupnum--
    ''',
    ]

    file_names=[]
    table_names=[]
    for job_command in job_commands:
        if job_command.__contains__("spark_group.py"):
            groups = job_command.split("hdfs://localhost:9000/input/spark_group.py")[1].split("--")
            filename = "group"+groups[1].strip().replace("\n","")
            table_name = groups[0].strip()
        else:
            values = job_command.split("hdfs://localhost:9000/input/spark_value.py")[1].split("--")
            yname = values[2].strip()
            if yname.__contains__(","):
                yname = ''.join(yname.split(","))
            date=""
            if len(values)>=4:
                date = values[3]
            filename = ("value" + values[1].strip()+yname.strip()+date.strip()).replace("\n","")
            table_name = values[0].strip()
        file_names.append(filename)
        table_names.append(table_name)
        run_spark_job_on_remote(job_command)

    for index,filename in enumerate(file_names):
        download_json(table_names[index],filename)

def download_json(tableName,filename):
    try:
        hdfs_output_path = f"/output/{tableName}/{filename}"
        local_output_path = os.path.join(parent_directory,f'{tableName}_{filename}.json')

        # 列出HDFS输出目录中的文件
        files = hadoop_client.list(hdfs_output_path)
        json_files = [f for f in files if f.startswith('part')]
        merged_data=[]
        if json_files:
            for json_file in json_files:
                hdfs_file_path = f"{hdfs_output_path}/{json_file}"
                try:
                    with hadoop_client.read(hdfs_file_path) as reader:
                        content = reader.read().decode('utf-8').strip()
                        if not content:
                            continue
                        for line in content.splitlines():
                            if line.strip():  # 忽略空行
                                merged_data.append(json.loads(line))
                except Exception as e:
                    print(f"e:{e}")
        print("merged_data:",merged_data)
        # 将合并后的数据写入本地文件
        with open(local_output_path, 'w', encoding='utf-8') as local_file:
            json.dump(merged_data, local_file, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"e:{e}")

def run_spark_job_on_remote(job_command):
    try:
        subprocess.run(job_command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing Hadoop job: {e}")

#spark分析
def spark_analyze(request):
    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code, "msg": "成功", "data": {}}
        try:
            upload_csv()
            send_cmd()
            return JsonResponse(msg, encoder=CustomJsonEncoder)
        except Exception as e:
            msg['code']=system_error_code
            msg['msg'] = f"发生错误：{e}"
            return JsonResponse(msg, encoder=CustomJsonEncoder)
