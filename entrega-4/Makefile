.PHONY: bootstrap infra build deploy verify status destroy help

SCRIPTS := scripts

help:
	@echo Targets: bootstrap infra build deploy verify status destroy
	@echo Requires: gcloud terraform docker kubectl make bash

bootstrap:
	bash $(SCRIPTS)/bootstrap.sh

infra:
	bash $(SCRIPTS)/infra.sh

build:
	bash $(SCRIPTS)/build-and-push.sh

deploy:
	bash $(SCRIPTS)/deploy-gcp.sh

verify:
	bash $(SCRIPTS)/verify-gcp.sh

status:
	-kubectl -n hda get pods,svc -o wide
	-terraform -chdir=infra/terraform output

destroy:
	bash $(SCRIPTS)/destroy.sh
