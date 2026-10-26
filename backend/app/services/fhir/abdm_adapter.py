from abc import ABC, abstractmethod

class ABHAProvider(ABC):
    @abstractmethod
    async def verify_abha(self, abha_id: str) -> bool:
        pass
        
    @abstractmethod
    async def get_patient_profile(self, abha_id: str) -> dict:
        pass

class DemoABHAProvider(ABHAProvider):
    async def verify_abha(self, abha_id: str) -> bool:
        # Fake implementation for SIH prototype
        return True
        
    async def get_patient_profile(self, abha_id: str) -> dict:
        return {
            "name": "Demo Patient",
            "gender": "M",
            "yearOfBirth": "1980"
        }

class ProductionABHAProvider(ABHAProvider):
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        
    async def verify_abha(self, abha_id: str) -> bool:
        # Requires actual UIDAI/ABDM gateway integration
        raise NotImplementedError("Production ABDM requires active Gateway keys")
        
    async def get_patient_profile(self, abha_id: str) -> dict:
        raise NotImplementedError("Production ABDM requires active Gateway keys")

class HISProvider(ABC):
    @abstractmethod
    async def sync_encounter(self, encounter_id: int, fhir_bundle: dict):
        pass

class DemoHISProvider(HISProvider):
    async def sync_encounter(self, encounter_id: int, fhir_bundle: dict):
        # Fake successful sync for SIH prototype
        print(f"Synced encounter {encounter_id} to Demo HIS")

class ProductionHISProvider(HISProvider):
    async def sync_encounter(self, encounter_id: int, fhir_bundle: dict):
        raise NotImplementedError("Production HIS integration required")
