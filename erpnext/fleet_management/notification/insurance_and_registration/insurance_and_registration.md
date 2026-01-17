<h3>Notification for Insurance Due</h3>

<p>Transaction {{ doc.name }} has due after a week which is on {{doc.due_date}}.</p>

<p><!-- show last comment -->
{% if comments %}
Last comment: {{ comments[-1].comment }} by {{ comments[-1].by }}
{% endif %}</p>

<h4>Details</h4>

<ul>
<li>Vehicle Number: {{ doc.registration_number }}
<li>Policy Number: {{ doc.policy_number }}
<li>Insured Date: {{ doc.insured_date }}
<li>Due Date: {{ doc.due_date }}
<li>Validity: {{ doc.validity }}
<li>Total Amount: {{ doc.total_amount }}
</ul>
