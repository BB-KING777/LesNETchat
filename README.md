# LesNETchat
This file is alfa and DO NOT reccomend to start.

IT's test for using Github.


## description
This is chat app to chatting in univ lesson.

# 日本語説明
これは授業中にチャットをするためのアプリケーションです。pythonで作成されています。本来はUDP broadcastで動的にサーバーを発見するつもりでしたが、大学のwifiをwiresharkで監視しながらUDPを垂れ流していたら、まったくUDPが流れてこなかったので、直打ちです。さすが、SNコースあるだけある。

https://github.com/BB-KING777/LesNETchat/issues/1#issue-2396060453

いい情報が得られたので、今後アップデートするかも

# アプリ説明
このアプリケーションは、サーバーとクライアントで動作します。シンプルなチャットアプリです。あまり多くチャットを送りすぎるとRAMを圧迫しますので、お気を付けください。なお、このRAM圧迫問題は1.0.3で解消する予定です。また、今後はファイルや画像を送信できるようにしたいと思っていますが、できる限り軽量な形を保持したいため、どうなるかは知りません。

distの中のexeファイルでやってください。

# 既知のバグ
- 稀に、とあるクライアントには送信され、とあるクライアントには送信されないメッセージが発生するバグ
- 異常に反映に時間のかかるメッセージが存在するバグ
