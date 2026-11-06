{% macro drop_ci_schema() %}

    {#- Safety guard: only ever drop schemas created for pull requests -#}
    {% if not target.schema.upper().startswith('CI_PR_') %}
        {{ exceptions.raise_compiler_error(
            "Refusing to drop schema " ~ target.schema ~ ": not a CI schema"
        ) }}
    {% endif %}

    {% set relation = target.database ~ "." ~ target.schema %}
    {% do run_query("drop schema if exists " ~ relation ~ " cascade") %}
    {{ log("Dropped schema " ~ relation, info=True) }}

{% endmacro %}