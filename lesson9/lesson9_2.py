import argparse
import random

def get_user_name()->str:
    """
    解析使用者姓名，優先從命令列參數取得，若未提供則互動式要求輸入。

    使用 argparse 接收 '-n' 或 '--name' 參數作為姓名，若未從命令列取得姓名，
    則會提示使用者輸入姓名。

    回傳:
        str: 使用者的姓名。
    """
    parser = argparse.ArgumentParser(description="猜數字遊戲")
    parser.add_argument("-n","--name",type=str,help="姓名")
    parser.add_argument("-f","--frequency",type=int,help="玩的次數",default=1)
    args = parser.parse_args()

    if not args.name:
        name = input("請輸入您的姓名:")
    else:
        name = args.name

    return name

def play_game(name:str)->None:
    """
    執行猜數字遊戲。
    這個函數會開始一個猜數字遊戲，玩家需要在1到100的範圍內猜測一個隨機生成的數字。
    遊戲會根據玩家的猜測提供提示（太大或太小），並動態調整猜測範圍，
    直到玩家猜中正確答案為止。
    Args:
        name (str): 玩家的名字，用於顯示遊戲過程中的訊息
    Returns:
        None: 此函數不返回任何值，直接在控制台進行互動
    Example:
        >>> play_game("小明")
        ========猜數字遊戲第1次=========
        42
        猜數字範圍1~100:50
        猜錯了!再小一點
        小明已經猜1次
        ...
    Note:
        - 遊戲會自動生成1到100之間的隨機目標數字
        - 玩家輸入超出當前範圍的數字時會提示重新輸入
        - 遊戲結束時會顯示總共猜測的次數
    """

    i = 0
    print(f"========猜數字遊戲第{i+1}次=========\n\n")
    min = 1
    max = 100
    count = 0
    target = random.randint(min,max)
    print(target)
    while(True):
        keyin = int(input(f"猜數字範圍{min}~{max}:"))
        count += 1
        if(keyin>=min and keyin<=max):
            if target == keyin:
                print(f"賓果!猜對了, 答案是:{target}")
                print(f"{name}共猜了{count}次\n")
                break
            elif(keyin > target):
                print(f"猜錯了!再小一點")
                max = keyin - 1
            else:
                print(f"猜錯了!再大一點")
                min = keyin + 1
            print(f"{name}已經猜{count}次\n")
        else:
            print("請輸入提示範圍內的數字\n")

def main():
    frequency = 1
    name = get_user_name()
    for i in range(frequency):
        play_game(name)
    print(f"遊戲結束,{name}共玩了{frequency}次")

if __name__ == '__main__':
    main()
