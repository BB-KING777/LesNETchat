import os
import json
import random
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

class BlackjackGame:
    def __init__(self, master):
        self.master = master
        self.master.title("Blackjack Game")
        
        self.card_images = {}
        self.load_images()
        
        self.deck = self.create_deck()
        self.player_hand = []
        self.dealer_hand = []
        
        self.points = self.load_points()
        self.bet = 10

        self.create_ui()
        self.reset_game()

    def load_images(self):
        directory = os.path.dirname(os.path.abspath(__file__))  # 現在のスクリプトがあるディレクトリを取得
        for filename in os.listdir(directory):
            if filename.endswith("@2x.png"):
                card_name = filename.replace('@2x.png', '')
                image_path = os.path.join(directory, filename)
                self.card_images[card_name] = ImageTk.PhotoImage(Image.open(image_path))
        self.card_images["back"] = ImageTk.PhotoImage(Image.open(os.path.join(directory, "back@2x.png")))

    def create_deck(self):
        suits = ['h', 'd', 'k', 's']
        values = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13']
        deck = [f"{suit}{value}" for suit in suits for value in values]
        random.shuffle(deck)
        return deck

    def create_ui(self):
        self.points_label = tk.Label(self.master, text=f"Points: {self.points}")
        self.points_label.pack(pady=10)

        self.bet_label = tk.Label(self.master, text=f"Bet: {self.bet}")
        self.bet_label.pack(pady=10)

        self.bet_slider = tk.Scale(self.master, from_=1, to=self.points, orient=tk.HORIZONTAL, command=self.update_bet)
        self.bet_slider.set(self.bet)
        self.bet_slider.pack(pady=10)

        self.dealer_frame = tk.Frame(self.master)
        self.dealer_frame.pack(pady=10)
        self.dealer_label = tk.Label(self.dealer_frame, text="Dealer's Hand")
        self.dealer_label.pack()
        self.dealer_total_label = tk.Label(self.dealer_frame, text="Dealer's Total: 0")
        self.dealer_total_label.pack()
        self.dealer_card_labels = []

        self.player_frame = tk.Frame(self.master)
        self.player_frame.pack(pady=10)
        self.player_label = tk.Label(self.player_frame, text="Player's Hand")
        self.player_label.pack()
        self.player_total_label = tk.Label(self.player_frame, text="Player's Total: 0")
        self.player_total_label.pack()
        self.player_card_labels = []

        self.result_label = tk.Label(self.master, text="", font=("Helvetica", 16))
        self.result_label.pack(pady=10)

        self.hit_button = tk.Button(self.master, text="Hit", command=self.hit)
        self.hit_button.pack(side=tk.LEFT, padx=10)
        
        self.stand_button = tk.Button(self.master, text="Stand", command=self.stand)
        self.stand_button.pack(side=tk.LEFT, padx=10)
        
        self.reset_button = tk.Button(self.master, text="Reset", command=self.reset_game)
        self.reset_button.pack(side=tk.LEFT, padx=10)

    def load_points(self):
        try:
            with open('points.json', 'r') as f:
                data = json.load(f)
                return data.get('points', 100)
        except (FileNotFoundError, json.JSONDecodeError):
            return 100

    def save_points(self):
        with open('points.json', 'w') as f:
            json.dump({'points': self.points}, f)

    def reset_game(self):
        self.deck = self.create_deck()
        self.player_hand = []
        self.dealer_hand = []
        self.player_hand.append(self.deck.pop())
        self.player_hand.append(self.deck.pop())
        self.dealer_hand.append(self.deck.pop())
        self.dealer_hand.append(self.deck.pop())
        self.result_label.config(text="")
        self.update_ui(initial=True)
        self.hit_button.config(state=tk.NORMAL)
        self.stand_button.config(state=tk.NORMAL)

    def update_ui(self, initial=False, reveal_dealer=False):
        for widget in self.dealer_frame.winfo_children():
            if widget != self.dealer_label and widget != self.dealer_total_label:
                widget.destroy()

        for widget in self.player_frame.winfo_children():
            if widget != self.player_label and widget != self.player_total_label:
                widget.destroy()

        self.dealer_card_labels = []
        for i, card in enumerate(self.dealer_hand):
            if initial and i != 0:
                card_label = tk.Label(self.dealer_frame, image=self.card_images["back"])
            else:
                if reveal_dealer or i == 0:
                    card_label = tk.Label(self.dealer_frame, image=self.card_images[card])
                else:
                    card_label = tk.Label(self.dealer_frame, image=self.card_images["back"])
            card_label.pack(side=tk.LEFT)
            self.dealer_card_labels.append(card_label)

        self.player_card_labels = [tk.Label(self.player_frame, image=self.card_images[card]) for card in self.player_hand]
        for card_label in self.player_card_labels:
            card_label.pack(side=tk.LEFT)

        self.dealer_total_label.config(text=f"Dealer's Total: {self.calculate_hand(self.dealer_hand, reveal_dealer)}")
        self.player_total_label.config(text=f"Player's Total: {self.calculate_hand(self.player_hand)}")

    def update_bet(self, value):
        self.bet = int(value)
        self.bet_label.config(text=f"Bet: {self.bet}")

    def hit(self):
        self.player_hand.append(self.deck.pop())
        self.update_ui()
        if self.calculate_hand(self.player_hand) > 21:
            self.end_game("Player busts! Dealer wins.", lose=True)

    def stand(self):
        self.update_ui(initial=False, reveal_dealer=True)  # Reveal all dealer cards
        self.dealer_ai()

    def dealer_ai(self):
        while self.calculate_hand(self.dealer_hand, reveal_dealer=True) < 17:
            self.dealer_hand.append(self.deck.pop())
            self.update_ui(initial=False, reveal_dealer=True)
        
        self.determine_winner()

    def calculate_hand(self, hand, reveal_dealer=False):
        total = 0
        aces = 0
        for card in hand:
            value = card[1:]
            if value in ['11', '12', '13']:
                total += 10
            elif value == '01':
                aces += 1
                total += 11
            else:
                total += int(value)
        
        while total > 21 and aces:
            total -= 10
            aces -= 1
        
        if reveal_dealer:
            return total
        else:
            return total if hand != self.dealer_hand else total - self.get_dealer_hidden_card_value()

    def get_dealer_hidden_card_value(self):
        hidden_card = self.dealer_hand[1]
        value = hidden_card[1:]
        if value in ['11', '12', '13']:
            return 10
        elif value == '01':
            return 11
        else:
            return int(value)

    def determine_winner(self):
        player_total = self.calculate_hand(self.player_hand, reveal_dealer=True)
        dealer_total = self.calculate_hand(self.dealer_hand, reveal_dealer=True)
        
        if dealer_total > 21 or player_total > dealer_total:
            self.end_game("Player wins!", win=True)
        elif player_total < dealer_total:
            self.end_game("Dealer wins!", lose=True)
        else:
            self.end_game("It's a tie!")

    def end_game(self, message, win=False, lose=False):
        if win:
            self.points += self.bet
        elif lose:
            self.points -= self.bet

        self.result_label.config(text=message)
        self.update_points()
        self.save_points()
        self.hit_button.config(state=tk.DISABLED)
        self.stand_button.config(state=tk.DISABLED)
        self.master.after(3000, self.reset_game)  # 3秒後にゲームをリセット

    def update_points(self):
        self.points_label.config(text=f"Points: {self.points}")
        self.bet_slider.config(to=self.points)
        if self.points <= 0:
            self.result_label.config(text="Game Over: You have run out of points!")
            self.hit_button.config(state=tk.DISABLED)
            self.stand_button.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    blackjack_game = BlackjackGame(root)
    root.mainloop()
