package io.opentelemetry.instrumentation.api.semconv;

class FirstAttributes {
  /**
  * short description of attr_one_a
  */
  public static final AttributeKey<Long> FIRST_ATTR_ONE_A = longKey("first.attr_one_a");

  /**
  * this is the description of attribute template
  */
  public static final AttributeKeyTemplate<String> FIRST_ATTR_TEMPLATE_ONE = stringKey("first.attr_template_one");

  /**
  * short description of last_attr last_attr with some special chars like {@code <key>} and an <a href="https://docs.oracle.com/en/java/javase/11/docs/api/java.management/java/lang/management/BufferPoolMXBean.html#getName()">url</a>.
  */
  public static final AttributeKey<Boolean> FIRST_LAST_ATTR = booleanKey("first.last_attr");
}