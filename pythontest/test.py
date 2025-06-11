from Bio import Entrez
from Bio import SeqIO
import time

# 设置你的邮箱（NCBI要求）
Entrez.email = "your_email@example.com"  # 替换为你的真实邮箱


def search_ncbi(query, max_results=5):
    """在NCBI中搜索条目"""
    print(f"\n搜索: {query}")
    handle = Entrez.esearch(db="nucleotide", term=query, retmax=max_results)
    record = Entrez.read(handle)
    handle.close()
    return record["IdList"]


def fetch_genbank_records(id_list):
    """获取GenBank记录"""
    ids = ",".join(id_list)
    handle = Entrez.efetch(db="nucleotide", id=ids, rettype="gb", retmode="text")
    records = list(SeqIO.parse(handle, "gb"))
    handle.close()
    return records


def fetch_abstract(pubmed_id):
    """获取PubMed摘要"""
    handle = Entrez.efetch(db="pubmed", id=pubmed_id, retmode="xml")
    record = Entrez.read(handle)
    handle.close()
    return record


def main():
    try:
        # 示例1: 搜索核苷酸序列
        query = "Homo sapiens[Organism] AND COX1[Gene]"
        ids = search_ncbi(query)
        print(f"找到的ID: {ids}")

        # 示例2: 获取GenBank记录
        if ids:
            records = fetch_genbank_records(ids[:2])  # 只取前两个
            for i, record in enumerate(records, 1):
                print(f"\n记录 {i}:")
                print(f"ID: {record.id}")
                print(f"描述: {record.description}")
                print(f"序列长度: {len(record.seq)} bp")
                # print(f"序列: {record.seq}")  # 取消注释查看完整序列

        # 示例3: 搜索PubMed文章
        pubmed_query = "COVID-19 vaccine"
        pubmed_ids = search_ncbi(pubmed_query, db="pubmed")
        if pubmed_ids:
            abstract = fetch_abstract(pubmed_ids[0])
            print("\nPubMed摘要示例:")
            print(abstract[0]['MedlineCitation']['Article']['Abstract']['AbstractText'][0])

    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        # NCBI要求不要频繁请求，每次请求后暂停
        time.sleep(1)


if __name__ == "__main__":
    main()