import asyncio
import logging
from potnanny.database import db
from potnanny.models.keychain import Keychain, KeychainSchema
from potnanny.models.license import License, LicenseSchema


logger = logging.getLogger(__name__)


async def load_license(data:dict):
    try:
        schema = LicenseSchema()
        clean = schema.load(data)
    except:
        return (1, "schema validation failure")

    async with db.transaction() as trx:
        try:
            license = await License.create(**clean)
            if 'actions' in data:
                if 'keychain_updates' in data['actions']:
                    for item in data['actions']['keychain_updates']:
                        kc = await Keychain.select().where(
                            Keychain.name == item['name']).first()
                        if kc:
                            kc.attributes.update(item['attributes'])
                            await kc.save()

                if 'keychain_creates' in data['actions']:
                    for item in data['actions']['keychain_creates']:
                        kc = await Keychain.create(**item)
                        await kc.save()

                if 'downloads' in data['actions']:
                    for item in data['actions']['downloads']:
                        pass

        except Exception as x:
            logger.warning(x)
            await trx.rollback()
            return (2, 'license insert failure')

    return (0, 'ok')
