select
  id,
  name,
  city,
  comments,
  "pii" as pii
from {{ ref('info') }}
