"""Mixin on ERPNext Lead. Dedup key and pipeline stage. CatBoost is not here."""

from erpatlas.pipeline.ingest import live_phone_key, normalize_phone


class AtlasLeadMixin:
	def validate(self):
		super().validate()
		phone = normalize_phone(self.get("mobile_no"))
		if phone:
			self.mobile_no = phone
		stage = self.get("atlas_stage") or "inquiry"
		self.atlas_stage = stage
		self.atlas_live_phone = live_phone_key(
			stage=stage,
			project=self.get("atlas_project") or "",
			phone=phone,
			lead_name=self.name,
		)
