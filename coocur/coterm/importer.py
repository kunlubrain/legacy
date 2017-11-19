import imp_pm_extract as extr
import imp_pm_tbl as tbl

def main():
    # 1. extract the papers
    extr.extractPapers(pubmedFile='?')

    # 2. make the tables
    tbl.makeSqlTable()

if __name__ == '__main__':
    main()
