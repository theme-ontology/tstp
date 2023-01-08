FROM docker.elastic.co/elasticsearch/elasticsearch:8.5.3 AS totolo-es

ENV node.name=es01
ENV cluster.name=es-docker-cluster
ENV bootstrap.memory_lock=true
ENV xpack.security.enabled=false
ENV discovery.type=single-node
#ENV ES_JAVA_OPTS="-Xms64m -Xmx128m"

CMD ["elasticsearch", "-Elogger.level=WARN"]
