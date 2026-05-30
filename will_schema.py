{
  "nbformat": 4,
  "nbformat_minor": 0,
  "metadata": {
    "colab": {
      "provenance": [],
      "authorship_tag": "ABX9TyO/9cH1F1jzj0bnlCnc7hQH",
      "include_colab_link": true
    },
    "kernelspec": {
      "name": "python3",
      "display_name": "Python 3"
    },
    "language_info": {
      "name": "python"
    }
  },
  "cells": [
    {
      "cell_type": "markdown",
      "metadata": {
        "id": "view-in-github",
        "colab_type": "text"
      },
      "source": [
        "<a href=\"https://colab.research.google.com/github/Madhura-55/Will_and_Legal_Succession_Planner/blob/main/will_schema.py\" target=\"_parent\"><img src=\"https://colab.research.google.com/assets/colab-badge.svg\" alt=\"Open In Colab\"/></a>"
      ]
    },
    {
      "cell_type": "code",
      "source": [
        "!pip install -q langchain langchain-anthropic python-dotenv pydantic"
      ],
      "metadata": {
        "id": "KNJRIcpw2CKg"
      },
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "code",
      "execution_count": 5,
      "metadata": {
        "id": "xiLHoam0uyP_"
      },
      "outputs": [],
      "source": [
        "from pydantic import BaseModel\n",
        "from typing import Optional, List\n",
        "\n",
        "class Asset(BaseModel):\n",
        "    asset_type: str\n",
        "    description: str\n",
        "    identifier: Optional[str] = None\n",
        "    estimated_value: Optional[float] = None\n",
        "\n",
        "class Beneficiary(BaseModel):\n",
        "    name: str\n",
        "    relationship: str\n",
        "    age: int\n",
        "    allocation: str\n",
        "    is_minor: bool = False\n",
        "\n",
        "class WillData(BaseModel):\n",
        "    testator_name: Optional[str] = None\n",
        "    testator_age: Optional[int] = None\n",
        "    testator_address: Optional[str] = None\n",
        "    religion: Optional[str] = None\n",
        "    family_type: Optional[str] = None\n",
        "    assets: List[Asset] = []\n",
        "    beneficiaries: List[Beneficiary] = []\n",
        "    executor_name: Optional[str] = None\n",
        "    executor_relationship: Optional[str] = None\n",
        "    witnesses: List[str] = []\n",
        "    minor_guardian: Optional[str] = None\n",
        "    residuary_beneficiary: Optional[str] = None"
      ]
    }
  ]
}