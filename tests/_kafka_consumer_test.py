# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import pytest

from data_pipeline._kafka_consumer import KafkaConsumer
from data_pipeline.expected_frequency import ExpectedFrequency
from tests.consumer_test import BaseConsumerTest
from tests.consumer_test import TIMEOUT


class TestKafkaConsumer(BaseConsumerTest):

    @pytest.fixture
    def publish_messages(self, producer, message, consumer):
        def _publish_messages(count):
            assert count > 0
            for _ in xrange(count):
                producer.publish(message)
            producer.flush()
        return _publish_messages

    @pytest.fixture(params=[
        {'decode_payload_in_workers': False},
        {'decode_payload_in_workers': True},
    ])
    def consumer_instance(self, request, topic, kafka_docker, team_name):
        return KafkaConsumer(
            consumer_name='test_consumer',
            team_name=team_name,
            expected_frequency_seconds=ExpectedFrequency.constantly,
            topic_to_consumer_topic_state_map={topic: None},
            decode_payload_in_workers=request.param['decode_payload_in_workers']
        )

    def test_get_messages_empty(self, consumer, topic,):
        messages = consumer.get_messages(count=10, blocking=True, timeout=TIMEOUT)
        assert len(messages) == 0
        assert consumer.topic_to_consumer_topic_state_map[topic] is None
