#!/usr/bin/fish

set targets (cat targets.list)

for t in $targets
    FLASK_APP=command flask target add $t
end
