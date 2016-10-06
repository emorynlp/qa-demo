echo "{" > config.json
echo "  \"backend_host\": \"127.0.0.1\"," >> config.json
echo "  \"backend_port\": \"9500\"," >> config.json
echo "" >> config.json
echo "  \"frontend_key\": \"<ENTER_YOUR_KEY>\"," >> config.json
echo "" >> config.json
echo "  \"elasticsearch_host\": \"127.0.0.1\"," >> config.json
echo "  \"elasticsearch_port\": \"9200\"," >> config.json
echo "  \"elasticsearch_index\": \"wikipedia_08\"," >> config.json
echo "  \"elasticsearch_type\": \"paragraph\"," >> config.json
echo "" >> config.json
echo "  \"word2vec_bin_file\": \"/Volumes/Transcend/Downloads/GoogleNews-vectors-negative300.bin\"" >> config.json
echo "}" >> config.json

mkdir pretrained_models/
wget --directory-prefix=pretrained_models/ http://www.mathcs.emory.edu/~tjurczy/qa-demo/pretrained.tar.gz
tar -xzvf pretrained_models/pretrained.tar.gz -C pretrained_models/
