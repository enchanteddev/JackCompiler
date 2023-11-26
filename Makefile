jack:
	python3 JackAnalyser.py ../Average/Main.jack
	python3 JackAnalyser.py ../ComplexArrays/Main.jack
	python3 JackAnalyser.py ../ConvertToBin/Main.jack
	python3 JackAnalyser.py ../Seven/Main.jack

	python3 JackAnalyser.py ../Square/Main.jack
	python3 JackAnalyser.py ../Square/SquareGame.jack
	python3 JackAnalyser.py ../Square/Square.jack
	python3 JackAnalyser.py ../Pong/Main.jack
	python3 JackAnalyser.py ../Pong/PongGame.jack
	python3 JackAnalyser.py ../Pong/Bat.jack
	python3 JackAnalyser.py ../Pong/Ball.jack

	mkdir -p ../Average/build
	mkdir -p ../ComplexArrays/build
	mkdir -p ../ConvertToBin/build
	mkdir -p ../Seven/build
	mkdir -p ../Square/build
	mkdir -p ../Pong/build

	mv ../Square/Main.new.vm ../Square/build/Main.vm
	mv ../Square/Square.new.vm ../Square/build/Square.vm
	mv ../Square/SquareGame.new.vm ../Square/build/SquareGame.vm

	mv ../Pong/Main.new.vm ../Pong/build/Main.vm
	mv ../Pong/Bat.new.vm ../Pong/build/Bat.vm
	mv ../Pong/Ball.new.vm ../Pong/build/Ball.vm
	mv ../Pong/PongGame.new.vm ../Pong/build/PongGame.vm
	
	mv ../Average/Main.new.vm ../Average/build/Main.vm
	mv ../Seven/Main.new.vm ../Seven/build/Main.vm
	mv ../ConvertToBin/Main.new.vm ../ConvertToBin/build/Main.vm
	mv ../ComplexArrays/Main.new.vm ../ComplexArrays/build/Main.vm