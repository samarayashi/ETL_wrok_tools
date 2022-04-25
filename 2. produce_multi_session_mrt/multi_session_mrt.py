import csv
import re
import xml.etree.ElementTree as ET
from dev_info import DevInfo
from utils.infa_constant import DOCUMENT_HEADER
from utils.wash_sql_query import wash_sql_query
from utils.tmp_null_filled.null_filled import get_new_sql_queries

TEMPLATE_MRT_NAME = "MULTI_SQL_TEMPLATE"
TEMPLATE_SESSION_NAME = "SESSION_TEMPLATE"
TEMPLATE_MAPPING_NAME = "TEMPLATE_MAPPING"


class MultiSqlMrtProducer:

    def __init__(self, template_export_xml: str, mrt_folder_name: str, template_workflow_name: str) -> ET.Element:
        """ get template workflow"""
        self.infa_export_tree = ET.parse(template_export_xml)
        self.powermart = self.infa_export_tree.getroot()
        self.wf_dev_folder = self.powermart.find(f'.//FOLDER[@NAME="{mrt_folder_name}"]')
        self.template_workflow = self.powermart.find(f'.//WORKFLOW[@NAME="{template_workflow_name}"]')

    def get_dev_info(self, csv_file_path: str):
        """read the csv with dev infomation, return a dict which already classified the information"""
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            info_objects = {}
            for row in reader:
                target_mrt_name = row["target_mrt_name"].strip()
                target_workflow_comment = row["target_workflow_comment"].strip()
                target_session_name = row["target_session_name"].strip()
                target_mapping_name = row["target_mapping_name"].strip()
                ori_sql_query = row["ori_sql_query"].strip()
                ori_columns = row["ori_columns"].strip()
                post_sql = wash_sql_query(row["post_sql"].strip())
                truncate_option = row["truncate_option"].strip().lower() == "yes"

                if target_mrt_name in info_objects:
                    existed_info: DevInfo
                    existed_info = info_objects[target_mrt_name]
                    existed_info.target_session_names.append(target_session_name)
                    existed_info.target_mapping_names.append(target_mapping_name)
                    existed_info.ori_sql_queries.append(ori_sql_query)
                    existed_info.all_ori_columns.append(ori_columns)
                    existed_info.post_sqls.append(post_sql)
                    existed_info.truncate_options.append(truncate_option)
                else:
                    info_objects[target_mrt_name] = DevInfo(target_mrt_name, target_workflow_comment,
                                                            target_session_name, target_mapping_name,
                                                            ori_sql_query, ori_columns, post_sql, truncate_option)

        return info_objects

    def replace_content_and_append(self, target_mrt_name: str, target_wf_comment: str,
                                   target_session_names: list[str], target_mapping_names: list[str],
                                   target_sql_queries: list[str], target_post_sqls: list[str],
                                   truncate_options: list[bool]) -> ET.Element:
        """convert the ET_element of template workflow into string, then replace template_string into target_string"""

        # count template have how many session
        template_count = 0
        all_sessions = self.template_workflow.findall('.//SESSION')
        for session in all_sessions:
            if session.attrib["NAME"].startswith("s_m_SESSION_TEMPLATE"):
                template_count += 1

        # convert ET_element to string
        template_workflow_string = ET.tostring(self.template_workflow).decode('utf-8')

        # replace the template mrt name to target mrt name
        dev_workflow_string = template_workflow_string.replace(TEMPLATE_MRT_NAME, target_mrt_name)

        #  replace session_name and mrt_name
        for session_list_index in range(len(target_session_names)):
            session_name_index = str(session_list_index+1)
            if session_list_index == len(target_session_names):
                dev_workflow_string = re.sub(TEMPLATE_SESSION_NAME + str(template_count) + r"\b",
                                             target_session_names[session_list_index], dev_workflow_string)
                dev_workflow_string = re.sub(TEMPLATE_MAPPING_NAME + str(template_count) + r"\b",
                                             target_mapping_names[session_list_index], dev_workflow_string)
                break
            dev_workflow_string = re.sub(TEMPLATE_SESSION_NAME + session_name_index + r"\b",
                                         target_session_names[session_list_index], dev_workflow_string)
            dev_workflow_string = re.sub(TEMPLATE_MAPPING_NAME + session_name_index + r"\b",
                                         target_mapping_names[session_list_index], dev_workflow_string)

        # turn back to xml element
        dev_workflow = ET.fromstring(dev_workflow_string)

        # update comment
        dev_workflow.set("DESCRIPTION", target_wf_comment)

        for session_index in range(len(target_session_names)):
            # get related element of target post_sql, pre_sql
            target_session_name = target_session_names[session_index]
            target_session = dev_workflow.find(f'.//SESSION[@NAME="s_m_{target_session_name}"]')
            target_defind = target_session.find('./SESSTRANSFORMATIONINST[@TRANSFORMATIONTYPE="Target Definition"]')
            source_defind = target_session.find('./SESSTRANSFORMATIONINST[@TRANSFORMATIONTYPE="Source Qualifier"]')
            souce_pre_sql_element = source_defind.find('./ATTRIBUTE[@NAME ="Sql Query"]')
            target_post_sql_element = target_defind.find('./ATTRIBUTE[@NAME="Post SQL"]')
            target_pre_sql_element = target_defind.find('./ATTRIBUTE[@NAME="Pre SQL"]')
            table_name = target_mapping_names[session_index]

            # add sql_query
            if souce_pre_sql_element is None:
                ET.SubElement(source_defind, "ATTRIBUTE",
                              {'NAME': 'Sql Query', 'VALUE': f'{target_sql_queries[session_index]}'})
            else:
                souce_pre_sql_element.set('VALUE', f'{target_sql_queries[session_index]}')

            # add value to target post_sql
            if target_post_sqls[session_index]:
                if target_post_sql_element is None:
                    ET.SubElement(target_defind, "ATTRIBUTE",
                                  {'NAME': 'Post SQL', 'VALUE': f'{target_post_sqls[session_index]}'})
                else:
                    target_post_sql_element.set('VALUE', f'{target_post_sqls[session_index]}')

            # add truncate to target pre_sql
            if truncate_options[session_index]:
                if target_pre_sql_element is None:
                    ET.SubElement(target_defind, "ATTRIBUTE",
                                  {'NAME': 'Pre SQL', 'VALUE': f"truncate table MX.{table_name}"})
                else:
                    ori_target_presql = target_pre_sql_element.get("VALUE")
                    fixed_target_presql = ori_target_presql + f"\ntruncate table MX.{table_name}"
                    target_pre_sql_element.set("VALUE", fixed_target_presql)

        self.wf_dev_folder.append(dev_workflow)

    def output_new_xml(self, output_file_path):
        data = ET.tostring(self.powermart)
        with open(output_file_path, "wb") as file:
            file.write(f"{DOCUMENT_HEADER}\n".encode(encoding="utf-8"))
            file.write(data)

if __name__ == "__main__":
    producer = MultiSqlMrtProducer(template_export_xml="source/multi_session_workflow_template.XML",
                                mrt_folder_name="MX_MRT", template_workflow_name="wf_MULTI_SQL_TEMPLATE")
    info_objs = producer.get_dev_info("source/mrt_multi_session_dev0930.csv")

    for info_obj in info_objs.values():
        info_obj: DevInfo

        new_queries = get_new_sql_queries(
            ori_sql_queries=info_obj.ori_sql_queries,
            all_ori_columns=info_obj.all_ori_columns
        )

        producer.replace_content_and_append(target_mrt_name=info_obj.target_mrt_name,
                                            target_wf_comment=info_obj.target_workflow_comment,
                                            target_session_names=info_obj.target_session_names,
                                            target_mapping_names=info_obj.target_mapping_names,
                                            target_sql_queries=new_queries,
                                            target_post_sqls=info_obj.post_sqls,
                                            truncate_options=info_obj.truncate_options)

    producer.output_new_xml("output/mrt_multi_session0930.xml")
