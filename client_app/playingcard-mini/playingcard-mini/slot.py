import tkinter as tk
from tkinter import messagebox
import random
import json
import os

class SlotGame:
    def __init__(self, master):
        self.master = master
        self.master.title("Emoji Slot Game")
        
        self.emojis = ['🍎', '🍊', '🍋', '🍉', '🍇', '🍒']
        
        self.load_points()
        self.bet = 10  # 初期の掛けポイント
        
        self.create_ui()
        
    def create_ui(self):
        self.label = tk.Label(self.master, text="Press Start to play")
        self.label.pack(pady=10)
        
        self.reel_labels = []
        self.reel_buttons = []
        self.reel_frames = []
        for i in range(3):
            frame = tk.Frame(self.master)
            frame.pack(side=tk.LEFT, padx=10)
            
            reel_label = tk.Label(frame, text="🍋", font=("Segoe UI Emoji", 40))  # 初期はレモンを表示
            reel_label.pack(pady=5)
            self.reel_labels.append(reel_label)
            
            reel_button = tk.Button(frame, text=f"Stop Reel {i+1}", command=lambda i=i: self.stop_reel(i))
            reel_button.pack(pady=5)
            self.reel_buttons.append(reel_button)
        
        self.start_button = tk.Button(self.master, text="Start", command=self.start_game)
        self.start_button.pack(pady=10)
        
        self.bet_label = tk.Label(self.master, text=f"Bet Points: {self.bet}")
        self.bet_label.pack(pady=10)
        
        self.bet_scale = tk.Scale(self.master, from_=10, to=50, orient=tk.HORIZONTAL, command=self.update_bet)
        self.bet_scale.set(self.bet)
        self.bet_scale.pack(pady=10)
        
        self.points_label = tk.Label(self.master, text=f"Points: {self.points}")
        self.points_label.pack(pady=10)
        
        self.result_label = tk.Label(self.master, text="")
        self.result_label.pack(pady=10)
        
        self.master.bind('<Return>', self.stop_game)  # Enterキーでリールを停止
        self.master.bind('1', lambda event: self.toggle_reel(0))  # 1キーでリール1を停止/開始
        self.master.bind('2', lambda event: self.toggle_reel(1))  # 2キーでリール2を停止/開始
        self.master.bind('3', lambda event: self.toggle_reel(2))  # 3キーでリール3を停止/開始
        self.master.bind('4', self.toggle_all_reels)  # 4キーですべてのリールを停止/開始
    
    def start_game(self, event=None):
        if self.points < self.bet:  # ポイントが足りない場合
            self.result_label.config(text="Not enough points to play!", fg="red")
            return
        
        self.points -= self.bet  # スタート時に掛けポイントを減らす
        self.update_points()
        self.label.config(text="Good luck!")
        self.result_label.config(text="")
        self.start_button.config(state=tk.DISABLED)  # スタートボタンを無効化
        
        # リールのアニメーションを開始
        self.reel_positions = [0, 0, 0]
        self.spinning = [True, True, True]
        self.spin_reels()
    
    def spin_reels(self):
        if any(self.spinning):
            self.update_reels()
            self.master.after(100, self.spin_reels)
        else:
            self.check_result()
            self.start_button.config(state=tk.NORMAL)  # スタートボタンを有効化
    
    def update_reels(self):
        for i in range(3):
            if self.spinning[i]:
                self.reel_labels[i].config(text=random.choice(self.emojis))
                self.reel_positions[i] += 1
    
    def stop_reel(self, reel_index):
        self.spinning[reel_index] = False
        if not any(self.spinning):
            self.check_result()
            self.start_button.config(state=tk.NORMAL)  # スタートボタンを有効化
    
    def start_reel(self, reel_index):
        self.spinning[reel_index] = True
        self.spin_reels()
    
    def toggle_reel(self, reel_index):
        if self.spinning[reel_index]:
            self.stop_reel(reel_index)
        else:
            self.start_reel(reel_index)
    
    def stop_game(self, event=None):
        self.spinning = [False, False, False]
        self.check_result()
        self.start_button.config(state=tk.NORMAL)  # スタートボタンを有効化
    
    def toggle_all_reels(self, event=None):
        if any(self.spinning):
            self.spinning = [False, False, False]
        else:
            self.spinning = [True, True, True]
            self.spin_reels()
    
    def check_result(self):
        result = [self.reel_labels[i].cget("text") for i in range(3)]
        if result[0] == result[1] == result[2]:
            self.points += self.bet * 10  # 同じ絵柄が揃った場合のポイント
            self.result_label.config(text=f"You win {self.bet * 10} points!", fg="green")
        elif result[0] == result[1] or result[1] == result[2] or result[0] == result[2]:
            self.points += self.bet  # 2つ揃った場合は掛けポイントを返す
            self.result_label.config(text=f"You get your bet of {self.bet} points back!", fg="blue")
        else:
            self.result_label.config(text="Try again!", fg="black")
        self.label.config(text="Press Start to play")
        self.update_points()
    
    def update_bet(self, value):
        self.bet = int(value)
        self.bet_label.config(text=f"Bet Points: {self.bet}")
    
    def update_points(self):
        self.points_label.config(text=f"Points: {self.points}")
        self.save_points()
    
    def load_points(self):
        if os.path.exists('points.json'):
            with open('points.json', 'r') as f:
                self.points = json.load(f).get('points', 100)
        else:
            self.points = 100
    
    def save_points(self):
        with open('points.json', 'w') as f:
            json.dump({'points': self.points}, f)
    
if __name__ == "__main__":
    root = tk.Tk()
    slot_game = SlotGame(root)
    root.mainloop()
