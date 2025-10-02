import { EndpointParameterInstructions } from "@smithy/middleware-endpoint";
import { Command as $Command } from "@smithy/smithy-client";
import {
  Handler,
  HttpHandlerOptions as __HttpHandlerOptions,
  MetadataBearer as __MetadataBearer,
  MiddlewareStack,
} from "@smithy/types";
import {
  CloudFrontClientResolvedConfig,
  ServiceInputTypes,
  ServiceOutputTypes,
} from "../CloudFrontClient";
import {
  ListCachePoliciesRequest,
  ListCachePoliciesResult,
} from "../models/models_1";
export { __MetadataBearer, $Command };
export interface ListCachePoliciesCommandInput
  extends ListCachePoliciesRequest {}
export interface ListCachePoliciesCommandOutput
  extends ListCachePoliciesResult,
    __MetadataBearer {}
export declare class ListCachePoliciesCommand extends $Command<
  ListCachePoliciesCommandInput,
  ListCachePoliciesCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: ListCachePoliciesCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: ListCachePoliciesCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<ListCachePoliciesCommandInput, ListCachePoliciesCommandOutput>;
  private serialize;
  private deserialize;
}
