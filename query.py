
# GraphQL query with operation name and variables

query = """
query domains($input: ListDomainsInput!) {
  domains(input: $input) {
    exactMatch {
      ...Domain
      __typename
    }
    list {
      ...Domain
      __typename
    }
    pageInfo {
      startCursor
      endCursor
      hasNextPage
      __typename
    }
    totalCount
    __typename
  }
}

fragment TldInfo on Tld {
  tldID
  tldName
  onChainID
  chainID
  chain
  creatorID
  baseContractAddr
  controllerAddr
  ownerAddr
  isVerified
  fullName
  __typename
}

fragment Domain on Domain {
  id
  name
  tokenId
  owner
  lastSalePrice
  listPrice
  expirationDate
  orderSource
  image
  tld {
    ...TldInfo
    __typename
  }
  __typename
}
"""