compile:
	@python3 JackAnalyser.py ../ArrayTest/Main.jack
	@python3 JackAnalyser.py ../ExpressionLessSquare/Main.jack
	@python3 JackAnalyser.py ../ExpressionLessSquare/Square.jack
	@python3 JackAnalyser.py ../ExpressionLessSquare/SquareGame.jack
	@python3 JackAnalyser.py ../Square/Main.jack
	@python3 JackAnalyser.py ../Square/Square.jack
	@python3 JackAnalyser.py ../Square/SquareGame.jack
	@echo "Compilation Done"

txml: compile
	@diff --strip-trailing-cr ../ArrayTest/MainT.xml ../ArrayTest/Main.new.xml
	@diff --strip-trailing-cr ../ExpressionLessSquare/MainT.xml ../ExpressionLessSquare/Main.new.xml
	@diff --strip-trailing-cr ../ExpressionLessSquare/SquareT.xml ../ExpressionLessSquare/Square.new.xml
	@diff --strip-trailing-cr ../ExpressionLessSquare/SquareGameT.xml ../ExpressionLessSquare/SquareGame.new.xml
	@diff --strip-trailing-cr ../Square/MainT.xml ../Square/Main.new.xml
	@diff --strip-trailing-cr ../Square/SquareT.xml ../Square/Square.new.xml
	@diff --strip-trailing-cr ../Square/SquareGameT.xml ../Square/SquareGame.new.xml
	@echo "All *T.xml files passed successfully."

xml: compile
	@diff --strip-trailing-cr ../ArrayTest/Main.xml ../ArrayTest/Main.f.xml
	@diff --strip-trailing-cr ../ExpressionLessSquare/Main.xml ../ExpressionLessSquare/Main.f.xml
	@diff --strip-trailing-cr ../ExpressionLessSquare/Square.xml ../ExpressionLessSquare/Square.f.xml
	@diff --strip-trailing-cr ../ExpressionLessSquare/SquareGame.xml ../ExpressionLessSquare/SquareGame.f.xml
	@diff --strip-trailing-cr ../Square/Main.xml ../Square/Main.f.xml
	@diff --strip-trailing-cr ../Square/Square.xml ../Square/Square.f.xml
	@diff --strip-trailing-cr ../Square/SquareGame.xml ../Square/SquareGame.f.xml
	@echo "All *.xml files passed successfully."