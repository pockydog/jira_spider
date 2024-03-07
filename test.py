import pandas as pd
import yaml


class PrometheusDealear:
    ouput_filepath = None
    OLD_MODULE = ''
    OLD_SERVER_NAME = ''
    OLD_IP_ADDRESS = ''
    OLD_PORT = ''

    @classmethod
    def _get_ouput_filepath(cls, file_path):
        if cls.ouput_filepath is None:
            cls.ouput_filepath = f"update_{file_path}"
            return f"update_{file_path}"

    @classmethod
    def _prometheus_csv_handle(cls, file_path, module_name='模块名称', server_name='服务器名称', ip_addr_name='IP地址',
                               port_name='Port'):
        cls._get_ouput_filepath(file_path=file_path)
        # 从CSV文件中读取数据，假设文件名为data.csv
        df = pd.read_csv(file_path)
        # 将空值填充为None
        df = df.fillna('')
        for index, row in df.iterrows():
            if not row[module_name]:
                df.at[index, module_name] = cls.OLD_MODULE
            else:
                cls.OLD_MODULE = row[module_name].strip()
            if not row[server_name]:
                df.at[index, server_name] = cls.OLD_SERVER_NAME
            else:
                cls.OLD_SERVER_NAME = row[server_name].strip()
            if not row[ip_addr_name]:
                df.at[index, ip_addr_name] = cls.OLD_IP_ADDRESS
            else:
                cls.OLD_IP_ADDRESS = row[ip_addr_name].strip()
            if not row[port_name]:
                df.at[index, 'Port'] = cls.OLD_PORT
            else:
                cls.OLD_PORT = row[port_name].strip()
        # 保存更新后的DataFrame回CSV文件
        # 保存更新后的DataFrame回CSV文件
        df.to_csv(cls.ouput_filepath, index=False)
        print(df)
        return True

    @classmethod
    def output_config(cls, file_path, module_name='模块名称', server_name='服务器名称', ip_addr_name='IP地址',
                      port_name='Port'):
        cls._prometheus_csv_handle(file_path, module_name, server_name, ip_addr_name, port_name)
        df = pd.read_csv(cls.ouput_filepath)
        node_exporter_data, black_box_exporter_data = dict(), dict()
        node_exporter_data['node_exporter'] = list()
        black_box_exporter_data['black_box_exporter'] = list()
        ip_set = set()
        for index, row in df.iterrows():
            ip_set.add(f"{row[ip_addr_name]}:9100")
            black_box_exporter_data['black_box_exporter'].append(f"{row[ip_addr_name]}:{row[port_name]}")
        node_exporter_data['node_exporter'] = list(ip_set)
        node_exporter_data_yaml = yaml.dump(node_exporter_data)
        black_box_exporter_data_yaml = yaml.dump(black_box_exporter_data)
        with open('node_exporter_data.yaml', 'w') as file:
            file.write(node_exporter_data_yaml)
        with open('black_box_exporter_data.yaml', 'w') as file:
            file.write(black_box_exporter_data_yaml)
        print(node_exporter_data_yaml)
        print(black_box_exporter_data_yaml)

    @classmethod
    def output_csv_to_it(cls, file_path, module_name='模块名称', server_name='服务器名称', ip_addr_name='IP地址',
                         port_name='Port'):
        cls._get_ouput_filepath(file_path)
        node_exporter_data = []
        tcp_exporter_data = []
        origin_ip = '10.160.1.14,10.160.0.2'
        reason = '業務'
        network_type = '內網VPN'
        df = pd.read_csv(cls.ouput_filepath)
        for index, row in df.iterrows():
            node_exporter_data.append({
                '源地址': origin_ip,
                '目標ip': row[ip_addr_name],
                '端口': 9100,
                '申請理由': reason,
                '網路類型': network_type
            })
            tcp_exporter_data.append({
                '源地址': origin_ip,
                '目標ip': row[ip_addr_name],
                '端口': row[port_name],
                '申請理由': reason,
                '網路類型': network_type
            })
        node_exporter_df = pd.DataFrame(node_exporter_data)
        # 创建并保存tcp_exporter_df
        tcp_exporter_df = pd.DataFrame(tcp_exporter_data)
        # 合并两个DataFrame
        combined_df = pd.concat([node_exporter_df, tcp_exporter_df], ignore_index=True)
        df_filtered = combined_df.groupby(['端口', '目標ip']).filter(lambda x: len(x) == 1)
        df_filtered.to_csv('網路申請開通.csv')
        print(df_filtered)


if __name__ == "__main__":
    # prometheus_dealear.output_config(filepath="g22-prod.csv",module_name='模块名称', server_name='服务器名称', ip_addr_name='IP地址',
    #          port_name='Port' )
    PrometheusDealear.output_csv_to_it(file_path="g22-prod.csv", module_name='模块名称', server_name='服务器名称',
                                        ip_addr_name='IP地址',
                                        port_name='Port')
