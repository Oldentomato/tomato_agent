#mac m1
# JAVA PATH
echo "export JAVA_HOME=/Library/Java/JavaVirtualMachines/zulu-15.jdk/Contents/Home" >> ~/.zshrc
echo "export PATH=${PATH}:$JAVA_HOME/bin:" >> ~/.zshrc
source ~/.zshrc

#ubuntu
# JAVA PATH
echo "export JAVA_HOME=/Library/Java/JavaVirtualMachines/zulu-15.jdk/Contents/Home" >> ~/.bashrc
echo "export PATH=${PATH}:$JAVA_HOME/bin:" >> ~/.bashrc
source ~/.bashrc