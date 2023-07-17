#python3 hyperedge_game_app/he-admin.py create-dataclass qeq2 Exp:UInt32 Level:UInt32
#python3 hyperedge_game_app/he-admin.py export
#python3 hyperedge_game_app/he-admin.py release 0.0.1-beta
python3 hyperedge_game_app/he-admin.py build 0.0.1-beta
#python3 hyperedge_game_app/he-admin.py create-env test
python3 hyperedge_game_app/he-admin.py run 0.0.1-beta test
