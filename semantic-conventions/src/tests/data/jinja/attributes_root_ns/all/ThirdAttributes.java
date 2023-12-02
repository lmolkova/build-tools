package io.opentelemetry.instrumentation.api.semconv;

class ThirdAttributes {
  /**
  * this is the description of attribute template
  */
  public static final AttributeKeyTemplate<String> THIRD_ATTR_TEMPLATE_THREE = stringKey("third.attr_template_three");

  /**
  * short description of attr_three
  */
  public static final AttributeKey<String> THIRD_ATTR_THREE = stringKey("third.attr_three");
}